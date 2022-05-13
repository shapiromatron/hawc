from django import forms

from hawc.apps.common.forms import BaseFormHelper

from ..common.admin import autocomplete
from . import models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study-population"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update an existing study-population."

    class Meta:
        exclude = ("study",)
        model = models.Design
        widgets = {
            "country": autocomplete(models.Design, "country", multi=True),
            "state": autocomplete(models.Design, "state", multi=True),
            "ecoregion": autocomplete(models.Design, "ecoregion", multi=True),
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        for fld in ("habitat_as_reported", "climate_as_reported"):
            self.fields[fld].widget.attrs["class"] = "html5text"
            self.fields[fld].widget.attrs["rows"] = 3

        if self.instance.id:
            helper = BaseFormHelper(self)
            helper.form_tag = False

        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text": self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.study.get_absolute_url(),
                "submit_text": "Next",
            }
            helper = BaseFormHelper(self, **inputs)

        helper.add_row("name", 3, "col-md-4")
        helper.add_row("country", 3, "col-md-4")
        helper.add_row("habitat", 4, "col-md-3")
        return helper


class CauseForm(forms.ModelForm):
    class Meta:
        exclude = ("study",)
        model = models.Cause
        widgets = {
            "study": autocomplete(models.Cause, "study"),
            "term": autocomplete(models.Cause, "term"),
            "measure": autocomplete(models.Cause, "measure"),
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None).study
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        for fld in ("measure_detail", "comment", "as_reported"):
            self.fields[fld].widget.attrs["class"] = "html5text"
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 6, "col-md-2")
        helper.add_row("level", 6, "col-md-2")
        helper.add_row("comment", 2, "col-md-6")
        return helper


class EffectForm(forms.ModelForm):
    class Meta:
        exclude = ("study",)
        model = models.Effect
        widgets = {
            "study": autocomplete(models.Effect, "study"),
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None).study
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        for fld in ("comment", "as_reported"):
            self.fields[fld].widget.attrs["class"] = "html5text"
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 3, "col-md-4")
        helper.add_row("measure_detail", 3, "col-md-4")
        helper.add_row("bio_org", 3, "col-md-4")
        return helper


class ResultForm(forms.ModelForm):
    class Meta:
        exclude = ("design",)
        model = models.Result
        widgets = {
            "design": autocomplete(models.Result, "design"),
            "cause": autocomplete(models.Result, "cause"),
            "effect": autocomplete(models.Result, "effect"),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        for fld in ("relationship_comment", "modifying_factors_comment", "description"):
            self.fields[fld].widget.attrs["class"] = "html5text"
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("cause", 6, "col-md-2")
        helper.add_row("modifying_factors_comment", 6, "col-md-2")
        helper.add_row("low_variability", 5, "col-md-2")
        return helper
