import logging

from crispy_forms import layout as cfl
from django import forms

from ..common.forms import BaseFormHelper
from . import models

logger = logging.getLogger(__name__)


class StudyLevelValueForm(forms.ModelForm):
    class Meta:
        model = models.StudyLevelValue
        exclude = ("study", "created", "last_updated")
        widgets = {}

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study
            self.instance.assessment = study.get_assessment()

        self.fields["comments"].widget.attrs["rows"] = 3

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.layout = cfl.Layout(
            cfl.Row(
                cfl.Column("system"),
            ),
            cfl.Row(
                cfl.Column("value_type"),
                cfl.Column("value"),
                cfl.Column("units"),
            ),
            cfl.Row(
                cfl.Column("comments"),
            ),
        )
        return helper
