from django import forms

from ..common.autocomplete import (
    AutocompleteMultipleChoiceField,
    AutocompleteChoiceField,
    AutocompleteTextWidget,
)
from ..common.forms import BaseFormHelper
from ..epi.autocomplete import CountryAutocomplete
from . import autocomplete, models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study design"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update an existing study design."

    country = AutocompleteMultipleChoiceField(autocomplete_class=CountryAutocomplete)
    state = AutocompleteMultipleChoiceField(autocomplete_class=autocomplete.StateAutocomplete)
    ecoregion = AutocompleteMultipleChoiceField(
        autocomplete_class=autocomplete.EcoregionAutocomplete
    )

    class Meta:
        exclude = ("study",)
        model = models.Design

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        for fld in ("habitat_as_reported", "climate_as_reported"):
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

    term = AutocompleteChoiceField(autocomplete_class=autocomplete.NestedTermAutocomplete)

    class Meta:
        exclude = ("study",)
        model = models.Cause

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.study = design.study

    @property
    def helper(self):
        for fld in ("comment", "as_reported"):
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 2, ["col-md-4", "col-md-8"])
        helper.add_row("bio_org", 4, "col-md-3")
        helper.add_row("level_units", 4, "col-md-3")
        helper.add_row("comment", 2, "col-md-6")
        return helper


class EffectForm(forms.ModelForm):

    term = AutocompleteChoiceField(autocomplete_class=autocomplete.NestedTermAutocomplete)

    class Meta:
        exclude = ("study",)
        model = models.Effect

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.study = design.study

    @property
    def helper(self):
        for fld in ("comment", "as_reported"):
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 2, ["col-md-4", "col-md-8"])
        helper.add_row("units", 3, "col-md-4")
        helper.add_row("comment", 2, "col-md-6")
        return helper


class ResultForm(forms.ModelForm):
    class Meta:
        exclude = ("design",)
        model = models.Result

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        for fld in ("relationship_comment", "modifying_factors_comment", "description"):
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("cause", 4, "col-md-3")
        helper.add_row("relationship_comment", 4, "col-md-3")
        helper.add_row("measure_type", 4, "col-md-3")
        helper.add_row("low_variability", 5, "col-md-2")
        return helper
