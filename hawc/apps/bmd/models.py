import json

from django.conf import settings
from django.db import models
from django.urls import reverse

from ..common.models import get_model_copy_name
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
        return reverse("bmd:assess_settings_detail", args=[self.assessment.pk])

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_default(cls, assessment):
        cls.objects.create(assessment=assessment)

    @property
    def can_create_sessions(self):
        return self.version == constants.BmdsVersion.BMDS330

    def copy_across_assessments(self, cw):
        old_id = self.id

        self.id = None
        self.assessment_id = cw[self.assessment.COPY_NAME][self.assessment_id]
        self.save()

        cw[get_model_copy_name(self)][old_id] = self.id


class LogicField(models.Model):
    objects = managers.LogicFieldManager()

    assessment = models.ForeignKey(
        "assessment.Assessment",
        on_delete=models.CASCADE,
        related_name="bmd_logic_fields",
        editable=False,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=30, editable=False)
    description = models.TextField(editable=False)
    failure_bin = models.PositiveSmallIntegerField(
        choices=constants.LogicBin.choices,
        blank=False,
        help_text="If the test fails, select the model-bin should the model be placed into.",
    )  # noqa
    threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="If a threshold is required for the test, threshold can be specified to non-default.",
    )  # noqa
    continuous_on = models.BooleanField(default=True, verbose_name="Continuous Datasets")
    dichotomous_on = models.BooleanField(default=True, verbose_name="Dichotomous Datasets")
    cancer_dichotomous_on = models.BooleanField(
        default=True, verbose_name="Cancer Dichotomous Datasets"
    )

    BREADCRUMB_PARENT = "assessment"

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse("bmd:assess_settings_detail", args=[self.assessment_id])

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_defaults(cls, assessment):
        """
        Build default BMD decision logic.
        """
        fn = str(settings.PROJECT_PATH / "apps/bmd/fixtures/logic.json")
        with open(fn, "r") as f:
            text = json.loads(f.read())

        objects = [cls(assessment_id=assessment.id, **obj) for i, obj in enumerate(text["objects"])]
        cls.objects.bulk_create(objects)

    def copy_across_assessments(self, cw):
        old_id = self.id

        self.id = None
        self.assessment_id = cw[self.assessment.COPY_NAME][self.assessment_id]
        self.save()

        cw[get_model_copy_name(self)][old_id] = self.id


class Session(models.Model):
    objects = managers.SessionManager()

    endpoint = models.ForeignKey(
        "animal.Endpoint", on_delete=models.CASCADE, related_name="bmd_sessions"
    )
    dose_units = models.ForeignKey(
        "assessment.DoseUnits", on_delete=models.CASCADE, related_name="bmd_sessions"
    )
    version = models.CharField(max_length=10, choices=constants.BmdsVersion.choices)
    bmrs = models.JSONField(default=list)
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
        return reverse("bmd:session_detail", args=[self.id])

    def get_update_url(self):
        return reverse("bmd:session_update", args=[self.id])

    def get_delete_url(self):
        return reverse("bmd:session_delete", args=[self.id])

    def get_api_url(self):
        return reverse("bmd:api:session-detail", args=[self.id])

    def get_execute_url(self):
        return reverse("bmd:api:session-execute", args=[self.id])

    def get_execute_status_url(self):
        return reverse("bmd:api:session-execute-status", args=[self.id])

    def get_selected_model_url(self):
        return reverse("bmd:api:session-selected-model", args=[self.id])

    @classmethod
    def create_new(cls, endpoint) -> "Session":
        dose_units = endpoint.get_doses_json(json_encode=False)[0]["id"]
        version = endpoint.assessment.bmd_settings.version
        return cls.objects.create(
            endpoint_id=endpoint.id, dose_units_id=dose_units, version=version
        )

    @property
    def is_finished(self):
        return self.date_executed is not None

    @property
    def can_edit(self):
        return self.version == constants.BmdsVersion.BMDS330

    def execute(self):
        raise NotImplementedError()

    def get_session(self, with_models=False):

        session = getattr(self, "_session", None)

        if session is None:
            dataset = bmd_interface.build_dataset(
                self.endpoint, dose_units_id=self.dose_units_id, n_drop_doses=self.n_drop_doses()
            )
            session = bmd_interface.build_session(dataset, self.version)
            self._session = session

        if with_models and not session.has_models:
            for model in self.models.all():
                session.add_model(model.name, overrides=model.overrides, id=model.id)

        return session

    def n_drop_doses(self) -> int:
        return max([0] + [model.overrides.get("dose_drop", 0) for model in self.models.all()])

    def get_model_options(self):
        return self.get_session().get_model_options()

    def get_bmr_options(self):
        return self.get_session().get_bmr_options()

    def get_selected_model(self):
        return SelectedModel.objects.filter(
            endpoint=self.endpoint_id, dose_units=self.dose_units_id
        ).first()

    def get_logic(self):
        return LogicField.objects.filter(assessment=self.endpoint.assessment_id)

    def get_study(self):
        return self.endpoint.get_study()


class Model(models.Model):
    objects = managers.ModelManager()

    IMAGE_UPLOAD_TO = "bmds_plot"

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="models")
    model_id = models.PositiveSmallIntegerField()
    bmr_id = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=25)
    overrides = models.JSONField(default=dict)
    date_executed = models.DateTimeField(null=True)
    execution_error = models.BooleanField(default=False)
    dfile = models.TextField(blank=True)
    outfile = models.TextField(blank=True)
    output = models.JSONField(default=dict)
    plot = models.ImageField(upload_to=IMAGE_UPLOAD_TO, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "created"
        ordering = ("model_id", "bmr_id")

    def get_absolute_url(self):
        return reverse("bmd:session_detail", args=[self.session_id])

    def get_assessment(self):
        return self.session.get_assessment()


class SelectedModel(models.Model):
    objects = managers.SelectedModelManager()

    endpoint = models.ForeignKey(
        "animal.Endpoint", on_delete=models.CASCADE, related_name="bmd_models"
    )
    dose_units = models.ForeignKey(
        "assessment.DoseUnits", on_delete=models.CASCADE, related_name="selected_models"
    )
    model = models.ForeignKey(Model, on_delete=models.CASCADE, null=True)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = "created"
        unique_together = (("endpoint", "dose_units"),)

    def get_assessment(self):
        return self.endpoint.get_assessment()
