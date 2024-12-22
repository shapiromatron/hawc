import traceback

import pybmds
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from reversion import revisions as reversion

from ..animal.models import Endpoint
from ..common.helper import ReportExport
from . import bmd_interface, constants, managers


class Session(models.Model):
    objects = managers.SessionManager()

    endpoint = models.ForeignKey(
        "animal.Endpoint", on_delete=models.CASCADE, related_name="bmd_sessions"
    )
    dose_units = models.ForeignKey(
        "assessment.DoseUnits", on_delete=models.CASCADE, related_name="bmd_sessions"
    )
    version = models.CharField(max_length=10)
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

    def get_report_url(self):
        return reverse("bmd:api:session-report", args=(self.id,))

    def get_execute_status_url(self):
        return reverse("bmd:api:session-execute-status", args=(self.id,))

    @classmethod
    def create_new(cls, endpoint: Endpoint) -> "Session":
        version = bmd_interface.version()
        inputs = constants.BmdInputSettings.create_default(endpoint)
        return cls.objects.create(
            endpoint_id=endpoint.id,
            dose_units_id=inputs.settings.dose_units_id,
            version=version,
            inputs=inputs.model_dump(),
            selected=constants.SelectedModel().model_dump(by_alias=True),
        )

    @property
    def is_finished(self) -> bool:
        return any(map(bool, [self.date_executed, self.outputs, self.errors]))

    @property
    def has_results(self) -> bool:
        return self.date_executed is not None and len(self.outputs) > 0

    def deactivate_similar_sessions(self):
        Session.objects.filter(endpoint=self.endpoint, dose_units=self.dose_units).exclude(
            id=self.id
        ).update(active=False)

    def execute(self):
        settings = self.get_settings()
        session = None
        try:
            session = bmd_interface.build_and_execute(self.endpoint, settings)
        except Exception:  # pragma: no cover
            self.errors = {"traceback": traceback.format_exc()}
        if session:
            self.outputs = session.to_dict()
        self.date_executed = timezone.now()
        self.save()

    def reset_execution(self):
        self.outputs = {}
        self.errors = {}
        self.selected = constants.SelectedModel().model_dump(by_alias=True)
        self.active = False
        self.date_executed = None

    def get_settings(self) -> constants.BmdInputSettings:
        return constants.BmdInputSettings.model_validate(self.inputs)

    def get_endpoint_serialized(self) -> dict:
        return self.endpoint.get_json(json_encode=False)

    def is_bmds_version2(self) -> bool:
        return self.version in {"BMDS2601", "BMDS270"}

    def get_study(self):
        return self.endpoint.get_study()

    def get_selected_model(self) -> dict:
        # Get selected model for endpoint representation
        selected = self.selected.copy()
        model = None
        if selected["version"] == 1:
            if model_id := self.selected.get("model_id"):
                model = [m for m in self.outputs["models"] if m["id"] == model_id][0]
                model["dose_units"] = self.dose_units_id
        elif selected["version"] == 2:
            if self.selected["model_index"] >= 0:
                index = self.selected["model_index"]
                model = self.outputs["models"][index]
                model["dose_units"] = self.dose_units_id
        selected.update(
            endpoint_id=self.endpoint_id,
            dose_units_id=self.dose_units_id,
            model=model,
            session_url=self.get_absolute_url(),
        )
        return selected

    def set_selected_model(self, selected: constants.SelectedModel):
        self.selected = selected.model_dump(by_alias=True)
        self.active = True
        self.outputs["selected"] = selected.to_bmd_output()

    def get_input_options(self) -> dict:
        return constants.get_input_options(self.endpoint.data_type)

    def get_session(self) -> pybmds.Session:
        if self.is_bmds_version2():
            raise ValueError("Cannot build session")
        return pybmds.Session.from_serialized(self.outputs)

    def create_report(self, request: HttpRequest) -> ReportExport:
        session = self.get_session()
        name = self.endpoint.name
        url = request.build_absolute_uri(self.get_absolute_url())
        versions = self.outputs["version"]
        return bmd_interface.create_report(session, name, url, versions)


reversion.register(Session)
