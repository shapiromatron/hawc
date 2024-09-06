from django import forms
from django.urls import reverse

from ..assessment.autocomplete import DSSToxAutocomplete
from ..common.autocomplete import (
    AutocompleteSelectMultipleWidget,
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)
from ..common.forms import ArrayCheckboxSelectMultiple, BaseFormHelper, QuillField
from ..common.widgets import SelectMultipleOtherWidget, SelectOtherWidget
from ..epi.autocomplete import CountryAutocomplete
from . import autocomplete, constants, models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study-population"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update an existing study-population."

    class Meta:
        model = models.Design
        exclude = ("study",)
        widgets = {
            "age_profile": ArrayCheckboxSelectMultiple(choices=constants.AgeProfile.choices),
            "countries": AutocompleteSelectMultipleWidget(autocomplete_class=CountryAutocomplete),
        }
        field_classes = {
            "criteria": QuillField,
            "susceptibility": QuillField,
            "comments": QuillField,
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

        helper.add_row("summary", 4, "col-md-3")
        helper.add_row("age_profile", 4, "col-md-3")
        helper.add_row("participant_n", 3, "col-md-4")
        helper.add_row("countries", 2, "col-md-4")
        helper.add_row("criteria", 3, "col-md-4")
        return helper


class ChemicalForm(forms.ModelForm):
    class Meta:
        model = models.Chemical
        exclude = ("design",)
        widgets = {
            "name": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ChemicalAutocomplete, field="name"
            ),
            "dsstox": AutocompleteSelectWidget(autocomplete_class=DSSToxAutocomplete),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        prefix = f"chemical-{kwargs.get("instance").pk if "instance" in kwargs else "-1"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 2, "col-md-6")
        helper.add_create_btn("dsstox", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        return helper


class ExposureForm(forms.ModelForm):
    class Meta:
        model = models.Exposure
        exclude = ("design",)
        widgets = {
            "measurement_type": SelectMultipleOtherWidget(
                choices=constants.MeasurementType.choices
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        prefix = f"exposure-{kwargs.get("instance").pk if "instance" in kwargs else "-1"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.set_textarea_height(("measurement_method", "comments"))
        helper.add_row("name", 2, "col-md-6")
        helper.add_row("biomonitoring_matrix", 2, "col-md-6")
        helper.add_row("measurement_timing", 4, "col-md-3")
        return helper


class ExposureLevelForm(forms.ModelForm):
    class Meta:
        model = models.ExposureLevel
        exclude = ("design",)
        widgets = {
            "units": AutocompleteTextWidget(
                autocomplete_class=autocomplete.ExposureLevelAutocomplete, field="units"
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        prefix = f"exposurelvl-{kwargs.get("instance").pk if "instance" in kwargs else "-1"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.design = design
        self.fields["chemical"].queryset = self.instance.design.chemicals.all()
        self.fields["exposure_measurement"].queryset = self.instance.design.exposures.all()

    def clean(self):
        data = super().clean()

        variance_type = data["variance_type"]
        variance = data["variance"]
        if variance and variance_type == constants.VarianceType.NA:
            msg = "A Variance Type must be selected when a value is given for Variance."
            self.add_error("variance_type", msg)

        ci_type = data["ci_type"]
        upper = data["ci_ucl"]
        lower = data["ci_lcl"]
        if (upper or lower) and ci_type == constants.ConfidenceIntervalType.NA:
            msg = "A Lower/Upper Interval Type must be selected when a value is given for the Lower or Upper interval."
            self.add_error("ci_type", msg)

        return data

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            help_text="The exposure levels entered in this subform will be linked to a specific result below. If exposure levels are reported separately for sub-populations (e.g., exposed and unexposed) and results are also reported separately, create a separate entry for each sub-population. If exposure levels are reported separately but results are reported for the full population, only one entry will be linked to the result, so information on the remaining sub-group may be captured in the comment field.",
        )
        helper.form_tag = False
        helper.set_textarea_height(("comments",))
        helper.add_row("name", 4, "col-md-3")
        helper.add_row("median", 5, ["col-md-2", "col-md-2", "col-md-2", "col-md-2", "col-md-4"])
        helper.add_row("ci_lcl", 5, ["col-md-2", "col-md-2", "col-md-2", "col-md-2", "col-md-4"])
        helper.add_row("negligible_exposure", 3, "col-md-4")
        return helper


class AdjustmentFactorForm(forms.ModelForm):
    class Meta:
        model = models.AdjustmentFactor
        exclude = ("design",)
        widgets = {"description": forms.Textarea}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        prefix = f"adjustmentfactor-{kwargs.get("instance").pk if "instance" in kwargs else "-1"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.set_textarea_height(("description", "comments"))
        helper.add_row("name", 3, "col-md-4")
        helper.form_tag = False
        return helper


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = models.Outcome
        exclude = ("design",)
        widgets = {
            "endpoint": AutocompleteTextWidget(
                autocomplete_class=autocomplete.OutcomeAutocomplete, field="endpoint"
            ),
            "effect": AutocompleteTextWidget(
                autocomplete_class=autocomplete.OutcomeAutocomplete, field="effect"
            ),
            "effect_detail": AutocompleteTextWidget(
                autocomplete_class=autocomplete.OutcomeAutocomplete, field="effect_detail"
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        prefix = f"outcome-{kwargs.get("instance").pk if "instance" in kwargs else "-1"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.set_textarea_height(("comments",))
        helper.add_row("system", 4, "col-md-3")
        helper.form_tag = False
        return helper


class DataExtractionForm(forms.ModelForm):
    class Meta:
        model = models.DataExtraction
        exclude = ("design",)
        widgets = {
            "exposure_transform": SelectOtherWidget(choices=constants.DataTransforms.choices),
            "outcome_transform": SelectOtherWidget(choices=constants.DataTransforms.choices),
            "effect_estimate_type": SelectOtherWidget(choices=constants.EffectEstimateType.choices),
            "confidence": AutocompleteTextWidget(
                autocomplete_class=autocomplete.DataExtractionAutocomplete, field="confidence"
            ),
            "units": AutocompleteTextWidget(
                autocomplete_class=autocomplete.DataExtractionAutocomplete, field="units"
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        prefix = f"extraction-{kwargs.get("instance").pk if "instance" in kwargs else "-1"}"
        super().__init__(*args, prefix=prefix, **kwargs)
        if design:
            self.instance.design = design
        self.fields["outcome"].queryset = self.instance.design.outcomes.all()
        self.fields["exposure_level"].queryset = self.instance.design.exposure_levels.all()
        self.fields["factors"].queryset = self.instance.design.adjustment_factors.all()

    def clean(self):
        data = super().clean()

        variance_type = data["variance_type"]
        variance = data["variance"]
        if variance and variance_type == constants.VarianceType.NA:
            msg = "A Variance Type must be selected when a value is given for Variance."
            self.add_error("variance_type", msg)

        ci_type = data["ci_type"]
        upper = data["ci_ucl"]
        lower = data["ci_lcl"]
        if (upper or lower) and ci_type == constants.ConfidenceIntervalType.NA:
            msg = "A Lower/Upper Bound Type must be selected when a value is given for the Lower or Upper bound."
            self.add_error("ci_type", msg)

        return data

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.set_textarea_height(("effect_description", "statistical_method", "comments"))
        helper.add_row("outcome", 4, "col-md-3")
        helper.add_row("effect_estimate_type", 6, "col-md-2")
        helper.add_row(
            "variance_type", 5, ["col-md-3", "col-md-2", "col-md-2", "col-md-2", "col-md-3"]
        )
        helper.add_row("group", 4, "col-md-3")
        helper.add_row("factors", 3, "col-md-4")
        helper.add_row("effect_description", 3, "col-md-4")
        helper.form_tag = False
        return helper
