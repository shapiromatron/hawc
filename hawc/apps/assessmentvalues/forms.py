from django import forms

from hawc.apps.assessmentvalues import models
from hawc.apps.common.forms import BaseFormHelper


class AssessmentValuesForm(forms.ModelForm):
    CREATE_LEGEND = "Create Assessment values"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update values for this Assessment."

    assessment = forms.Field(disabled=True, widget=forms.HiddenInput)

    class Meta:
        model = models.AssessmentValues
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment

    @property
    def helper(self):
        self.fields["comments"].widget.attrs["class"] = "html5text"
        self.fields["comments"].widget.attrs["rows"] = 3

        if self.instance.id:
            helper = BaseFormHelper(self, help_text=self.UPDATE_HELP_TEXT)

        else:
            helper = BaseFormHelper(
                self,
                legend_text=self.CREATE_LEGEND,
                help_text=self.CREATE_HELP_TEXT,
                cancel_url=self.instance.assessment.get_absolute_url(),
            )

        return helper
