from django import forms
from django.urls import reverse

from hawc.apps.common.dynamic_forms.schemas import Schema
from hawc.apps.common.forms import BaseFormHelper, PydanticValidator

from .models import CustomDataExtraction


class CustomDataExtractionForm(forms.ModelForm):
    schema = forms.JSONField(
        initial=Schema(fields=[]).dict(),
        validators=[PydanticValidator(Schema)],
    )

    class Meta:
        model = CustomDataExtraction
        exclude = ("created", "last_updated")

    @property
    def helper(self):
        cancel_url = reverse("portal")  # TODO: replace temp cancel url
        helper = BaseFormHelper(
            self,
            legend_text="Create a custom data extraction form",
            cancel_url=cancel_url,
            submit_text="Create Form",
        )
        return helper
