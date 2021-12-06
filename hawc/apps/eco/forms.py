from django import forms

from ..common.admin import autocomplete
from . import models


class MetadataForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Metadata
        widgets = {
            "study": autocomplete(models.Metadata, "study"),
            "country": autocomplete(models.Metadata, "country", multi=True),
            "state": autocomplete(models.Metadata, "state", multi=True),
            "ecoregion": autocomplete(models.Metadata, "ecoregion", multi=True),
        }


class CauseForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Cause
        widgets = {
            "study": autocomplete(models.Cause, "study"),
        }


class EffectForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Effect
        widgets = {
            "cause": autocomplete(models.Effect, "cause"),
        }


class QuantitativeForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Quantitative
        widgets = {
            "effect": autocomplete(models.Quantitative, "effect"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            for field, value, in self.instance.default_related().items():
                self.fields[field].initial = value
