from django import forms

from . import models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study-population"

    CREATE_HELP_TEXT = ""

    UPDATE_HELP_TEXT = "Update an existing study-population."

    class Meta:
        model = models.Design
        exclude = ("study",)
        labels = {}
