from django import forms
from django.urls import reverse_lazy

from ..common.autocomplete import (
    AutocompleteSelectMultipleWidget,
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)
from ..common.forms import BaseFormHelper
from ..common.helper import new_window_a
from ..epi.autocomplete import CountryAutocomplete
from . import autocomplete, models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study design"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update an existing study design."

    class Meta:
        exclude = ("study",)
        model = models.Design
        widgets = {
            "countries": AutocompleteSelectMultipleWidget(autocomplete_class=CountryAutocomplete),
            "states": AutocompleteSelectMultipleWidget(
                autocomplete_class=autocomplete.StateAutocomplete
            ),
            "ecoregions": AutocompleteSelectMultipleWidget(
                autocomplete_class=autocomplete.EcoregionAutocomplete
            ),
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        for fld in ("habitats_as_reported", "climates_as_reported", "comments"):
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
        helper.add_row("countries", 3, "col-md-4")
        helper.add_row("habitats", 4, "col-md-3")
        return helper


def _term_help_text():
    a = new_window_a(reverse_lazy("eco:term_list"), "term list")
    return f"Controlled vocabulary term; view entire {a}. Select a term by name or numeric ID."


class CauseForm(forms.ModelForm):
    class Meta:
        exclude = ("study",)
        model = models.Cause
        widgets = {
            "term": AutocompleteSelectWidget(
                autocomplete_class=autocomplete.NestedTermAutocomplete
            ),
            "species": AutocompleteTextWidget(
                autocomplete_class=autocomplete.CauseAutocomplete, field="species"
            ),
            "level_units": AutocompleteTextWidget(
                autocomplete_class=autocomplete.CauseAutocomplete, field="level_units"
            ),
            "duration": AutocompleteTextWidget(
                autocomplete_class=autocomplete.CauseAutocomplete, field="duration"
            ),
            "duration_units": AutocompleteTextWidget(
                autocomplete_class=autocomplete.CauseAutocomplete, field="duration_units"
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.study = design.study

    @property
    def helper(self):
        for fld in ("as_reported", "comments", "level"):
            self.fields[fld].widget.attrs["rows"] = 3

        self.fields["term"].help_text = _term_help_text()

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 2, ["col-md-4", "col-md-8"])
        helper.add_row("biological_organization", 2, "col-md-6")
        helper.add_row("level", 3, ["col-md-6", "col-md-3", "col-md-3"])
        helper.add_row("duration", 3, "col-md-4")
        helper.add_row("exposure", 3, "col-md-4")
        helper.add_row("as_reported", 2, "col-md-6")
        return helper


class EffectForm(forms.ModelForm):
    class Meta:
        exclude = ("study",)
        model = models.Effect
        widgets = {
            "term": AutocompleteSelectWidget(
                autocomplete_class=autocomplete.NestedTermAutocomplete
            ),
            "species": AutocompleteTextWidget(
                autocomplete_class=autocomplete.EffectAutocomplete, field="species"
            ),
            "units": AutocompleteTextWidget(
                autocomplete_class=autocomplete.EffectAutocomplete, field="units"
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.study = design.study

    @property
    def helper(self):
        for fld in ("as_reported", "comments"):
            self.fields[fld].widget.attrs["rows"] = 3

        self.fields["term"].help_text = _term_help_text()

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 2, ["col-md-4", "col-md-8"])
        helper.add_row("biological_organization", 3, "col-md-4")
        helper.add_row("as_reported", 2, "col-md-6")
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
        for fld in ("relationship_comment", "modifying_factors_comment", "comments"):
            self.fields[fld].widget.attrs["rows"] = 3

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 4, ["col-md-4", "col-md-3", "col-md-3", "col-md-2"])
        helper.add_row("relationship_direction", 2, "col-md-6")
        helper.add_row("measure_type", 4, "col-md-3")
        helper.add_row("variability", 3, "col-md-4")
        helper.add_row("modifying_factors", 2, "col-md-6")
        helper.add_row("statistical_sig_type", 3, "col-md-4")
        return helper
