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
