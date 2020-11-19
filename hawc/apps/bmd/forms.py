from django.forms import ModelForm

from ..common.forms import BaseFormHelper
from . import models


class AssessmentSettingsForm(ModelForm):
    class Meta:
        model = models.AssessmentSettings
        exclude = ("assessment",)

    @property
    def helper(self):
        return BaseFormHelper(
            self,
            legend_text="Update BMD settings",
            help_text="Update BMD assessment settings. These are applied globally across the entire assessment.",
            cancel_url=self.instance.get_absolute_url(),
        )


class LogicFieldForm(ModelForm):
    class Meta:
        model = models.LogicField
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.threshold is None:
            self.fields.pop("threshold")

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text=f"Update BMD Logic: {self.instance.name}",
            help_text=self.instance.description,
            cancel_url=self.instance.assessment.bmd_settings.get_absolute_url(),
        )
        if "threshold" in self.fields:
            helper.add_row("failure_bin", 2, "col-md-6")
        helper.add_row("continuous_on", 3, "col-md-4")
        return helper


class SessionForm(ModelForm):
    class Meta:
        model = models.Session
        fields = "__all__"
