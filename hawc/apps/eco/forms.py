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

        helper.set_textarea_height(("habitats_as_reported", "climates_as_reported", "comments"))
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
        prefix = f"cause-{kwargs.get("instance").pk if "instance" in kwargs else "new"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.study = design.study

    @property
    def helper(self):
        self.fields["term"].help_text = _term_help_text()

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.set_textarea_height(("as_reported", "comments", "level"))
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
        prefix = f"effect-{kwargs.get("instance").pk if "instance" in kwargs else "new"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.study = design.study

    @property
    def helper(self):
        self.fields["term"].help_text = _term_help_text()

        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.set_textarea_height(("as_reported", "comments"))
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
        prefix = f"result-{kwargs.get("instance").pk if "instance" in kwargs else "new"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.design = design
        self.fields["cause"].queryset = self.fields["cause"].queryset.filter(
            study_id=self.instance.design.study_id
        )
        self.fields["effect"].queryset = self.fields["effect"].queryset.filter(
            study_id=self.instance.design.study_id
        )

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.set_textarea_height(
            ("relationship_comment", "modifying_factors_comment", "comments")
        )
        helper.add_row("name", 4, ["col-md-4", "col-md-3", "col-md-3", "col-md-2"])
        helper.add_row(
            "relationship_direction", 4, ["col-md-2", "col-md-4", "col-md-3", "col-md-3"]
        )
        helper.add_row("modifying_factors", 2, "col-md-6")
        helper.add_row("measure_type", 4, "col-md-3")
        helper.add_row("variability", 4, ["col-md-2", "col-md-2", "col-md-2", "col-md-6"])
        return helper

    RESPONSE_VARIABILITY_REQ = (
        "Response variability is required if a lower or upper response measure is given."
    )

    def clean(self):
        cleaned_data = super().clean()

        resp_var = cleaned_data.get("variability")
        lower_measure = cleaned_data.get("low_variability")
        upper_measure = cleaned_data.get("upper_variability")
        if (lower_measure or upper_measure) and not resp_var:
            self.add_error("variability", self.RESPONSE_VARIABILITY_REQ)

        return cleaned_data
