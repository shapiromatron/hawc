from django import forms

from ..common.admin import autocomplete
from . import models


class DesignForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Design
        widgets = {
            "study": autocomplete(models.Design, "study"),
            "countries": autocomplete(models.Design, "countries", multi=True),
            "state": autocomplete(models.Design, "state", multi=True),
            "ecoregion": autocomplete(models.Design, "ecoregion", multi=True),
        }


class CauseForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Cause
        widgets = {
            "study": autocomplete(models.Cause, "study"),
            "term": autocomplete(models.Cause, "term"),
            "measure": autocomplete(models.Cause, "measure"),
        }


class EffectForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Effect
        widgets = {
            "study": autocomplete(models.Effect, "study"),
        }


class ResultForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.Result
        widgets = {
            "study": autocomplete(models.Result, "study"),
            "design": autocomplete(models.Result, "design"),
            "cause": autocomplete(models.Result, "cause"),
            "effect": autocomplete(models.Result, "effect"),
        }
