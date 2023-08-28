from django import forms
from models import CustomDataExtraction

from hawc.apps.common.dynamic_forms.schemas import Schema
from hawc.apps.common.forms import PydanticValidator


class CustomDataExtractionForm(forms.ModelForm):
    schema = forms.JSONField(
        initial=Schema(fields=[]).dict(),
        validators=[PydanticValidator(Schema)],
    )

    class Meta:
        model = CustomDataExtraction
        exclude = ("created", "last_updated")
