from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect, AutocompleteSelectMultiple

from . import models


def autocomplete(Model, field: str, multi: bool = False):
    Widget = AutocompleteSelectMultiple if multi else AutocompleteSelect
    return Widget(Model._meta.get_field(field), admin.site)


class EcoMetadataForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = models.EcoMetadata
        widgets = {
            "study": autocomplete(models.EcoMetadata, "study"),
            "country": autocomplete(models.EcoMetadata, "country", multi=True),
            "state": autocomplete(models.EcoMetadata, "state", multi=True),
            "ecoregion": autocomplete(models.EcoMetadata, "ecoregion", multi=True),
        }
