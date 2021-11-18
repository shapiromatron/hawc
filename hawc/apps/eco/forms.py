from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect, AutocompleteSelectMultiple

from . import models


def autocomplete(Model, field: str, multi: bool = False):
    Widget = AutocompleteSelectMultiple if multi else AutocompleteSelect
    return Widget(Model._meta.get_field(field), admin.site)


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
