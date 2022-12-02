import traceback
from typing import Type

from django.db import models
from django.urls import reverse
from django.utils import timezone
from pydantic import BaseModel

from ..animal.constants import DataType
from ..animal.models import Endpoint
from . import bmd_interface, constants, managers


class AssessmentSettings(models.Model):
    objects = managers.AssessmentSettingsManager()

    assessment = models.OneToOneField(
        "assessment.Assessment", on_delete=models.CASCADE, related_name="bmd_settings"
    )
    version = models.CharField(
        max_length=10,
        choices=constants.BmdsVersion.choices,
        default=constants.BmdsVersion.BMDS330,
        help_text="Select the BMDS version to be used for dose-response modeling. Version 2 is no longer supported for execution; but results will be available for any version after execution is complete.",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        verbose_name_plural = "BMD settings"

    def __str__(self):
        return "BMD settings"

    def get_absolute_url(self):
        return reverse("bmd:assess_settings_detail", args=(self.assessment_id,))

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_default(cls, assessment):
        cls.objects.create(assessment=assessment)

    @property
    def can_create_sessions(self):
        return self.version.startswith("BMDS3")


class Session(models.Model):
    objects = managers.SessionManager()

    endpoint = models.ForeignKey(
        "animal.Endpoint", on_delete=models.CASCADE, related_name="bmd_sessions"
    )
    dose_units = models.ForeignKey(
        "assessment.DoseUnits", on_delete=models.CASCADE, related_name="bmd_sessions"
    )
    version = models.CharField(max_length=10, choices=constants.BmdsVersion.choices)
    inputs = models.JSONField(default=dict)
    outputs = models.JSONField(default=dict)
    errors = models.JSONField(default=dict)
    selected = models.JSONField(default=dict)
    active = models.BooleanField(default=False)
    date_executed = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "endpoint"

    class Meta:
        verbose_name_plural = "BMD sessions"
        get_latest_by = "last_updated"
        ordering = ("-last_updated",)

    def __str__(self):
        return "BMD session"

    def get_assessment(self):
        return self.endpoint.get_assessment()

    def get_absolute_url(self):
        return reverse("bmd:session_detail", args=(self.id,))

    def get_update_url(self):
        return reverse("bmd:session_update", args=(self.id,))

    def get_delete_url(self):
        return reverse("bmd:session_delete", args=(self.id,))

    def get_api_url(self):
        return reverse("bmd:api:session-detail", args=(self.id,))

    def get_execute_status_url(self):
        return reverse("bmd:api:session-execute-status", args=(self.id,))

    @classmethod
    def create_new(cls, endpoint: Endpoint) -> "Session":
        if not endpoint.assessment.bmd_settings.can_create_sessions:
            raise ValueError("Cannot create new analysis")
        dose_units_id = endpoint.get_doses_json(json_encode=False)[0]["id"]
        version = endpoint.assessment.bmd_settings.version

        if endpoint.data_type == DataType.CONTINUOUS:
            inputs = constants.ContinuousInputSettings(dose_units_id=dose_units_id)
        elif endpoint.data_type in [DataType.DICHOTOMOUS, DataType.DICHOTOMOUS_CANCER]:
            inputs = constants.DichotomousInputSettings(dose_units_id=dose_units_id)
        else:
            raise ValueError("Cannot create new analysis")

        return cls.objects.create(
            endpoint_id=endpoint.id,
            dose_units_id=dose_units_id,
            version=version,
            inputs=inputs.dict(),
        )

    @property
    def is_finished(self) -> bool:
        return any(map(bool, [self.date_executed, self.outputs, self.errors]))

    @property
    def can_edit(self):
        return self.version.startswith("BMDS3")

    def execute(self):
        settings = self.get_settings()
        try:
            session = bmd_interface.build_and_execute(self.endpoint, settings)
            self.outputs = session.to_dict()
        except Exception:
            self.errors = {"traceback": traceback.format_exc()}
        self.date_executed = timezone.now()
        self.save()

    def set_selected_model(self):
        pass

    def get_settings(self) -> Type[BaseModel]:
        return constants.get_input_model(self.endpoint).parse_obj(self.inputs)

    def get_session(self, with_models=False):

        session = getattr(self, "_session", None)

        if session is None:
            dataset = bmd_interface.build_dataset(
                self.endpoint, dose_units_id=self.dose_units_id, n_drop_doses=self.n_drop_doses()
            )
            session = bmd_interface.build_session(dataset, constants.BmdsVersion(self.version))
            self._session = session

        if with_models and not session.has_models:
            for model in self.models.all():
                session.add_model(model.name, overrides=model.overrides, id=model.id)

        return session

    def n_drop_doses(self) -> int:
        return max(
            [0] + [model["overrides"].get("dose_drop", 0) for model in self.outputs["models"]]
        )

    def get_model_options(self):
        return self.get_session().get_model_options()

    def get_bmr_options(self):
        return self.get_session().get_bmr_options()

    def get_study(self):
        return self.endpoint.get_study()

    def get_selected_model(self) -> dict:
        # Get selected model for endpoint representation
        selected = self.selected.copy()
        model = None
        if model_id := self.selected["model_id"]:
            model = [m for m in self.outputs["models"] if m["id"] == model_id][0]
            model["dose_units"] = self.dose_units_id
        selected.update(
            endpoint_id=self.endpoint_id,
            dose_units_id=self.dose_units_id,
            model=model,
            session_url=self.get_absolute_url(),
        )
        return selected

    def get_input_options(self) -> dict:
        return constants.get_input_options(self.endpoint.data_type)
