from django import forms

from hawc.apps.common.dynamic_forms.schemas import Schema
from hawc.apps.common.forms import PydanticValidator

from .models import CustomDataExtraction


class CustomDataExtractionForm(forms.ModelForm):
    schema = forms.JSONField(
        initial=Schema(fields=[]).dict(),
        validators=[PydanticValidator(Schema)],
    )

    class Meta:
        model = CustomDataExtraction
        exclude = ("created", "last_updated")
