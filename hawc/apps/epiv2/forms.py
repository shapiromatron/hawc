from django import forms
from django.urls import reverse

from hawc.apps.common.forms import BaseFormHelper

from ..assessment.lookups import DssToxIdLookup
from ..common import selectable
from ..common.forms import ArrayCheckboxSelectMultiple
from ..common.widgets import SelectMultipleOtherWidget, SelectOtherWidget
from . import constants, lookups, models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study-population"
    CREATE_HELP_TEXT = ""
    UPDATE_HELP_TEXT = "Update an existing study-population."

    countries = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.CountryNameLookup, required=False
    )

    class Meta:
        model = models.Design
        exclude = ("study",)
        widgets = {"age_profile": ArrayCheckboxSelectMultiple(choices=constants.AgeProfile.choices)}

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        for fld in ("criteria", "susceptibility", "comments"):
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

        helper.add_row("summary", 4, "col-md-3")
        helper.add_row("age_profile", 4, "col-md-3")
        helper.add_row(
            "participant_n", 5, ["col-md-2", "col-md-2", "col-md-2", "col-md-2", "col-md-4"]
        )
        helper.add_row("criteria", 3, "col-md-4")
        return helper


class ChemicalForm(forms.ModelForm):
    class Meta:
        model = models.Chemical
        exclude = ("design",)
        widgets = {
            "name": selectable.AutoCompleteWidget(
                lookup_class=lookups.ChemicalNameLookup, allow_new=True
            ),
            "dsstox": selectable.AutoCompleteSelectWidget(lookup_class=DssToxIdLookup),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
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
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        for fld in ["measurement_method", "comments"]:
            self.fields[fld].widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 2, "col-md-6")
        helper.add_row("biomonitoring_matrix", 2, "col-md-6")
        helper.add_row("measurement_timing", 4, "col-md-3")
        return helper


class ExposureLevelForm(forms.ModelForm):
    class Meta:
        model = models.ExposureLevel
        exclude = ("design",)
        widgets = {
            "units": selectable.AutoCompleteWidget(
                lookup_class=lookups.ExposureLevelUnitsLookup, allow_new=True
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design
        self.fields["chemical"].queryset = self.instance.design.chemicals.all()
        self.fields["exposure_measurement"].queryset = self.instance.design.exposures.all()

    def clean_variance_type(self):
        data = self.cleaned_data["variance_type"]
        variance = self.cleaned_data.get("variance")
        if variance and data == constants.VarianceType.NONE:
            raise forms.ValidationError(
                "A Variance Type must be selected when a value is given for Variance."
            )
        return data

    def clean_ci_type(self):
        data = self.cleaned_data["ci_type"]
        upper = self.cleaned_data.get("ci_ucl")
        lower = self.cleaned_data.get("ci_lcl")
        if (upper or lower) and data == constants.ConfidenceIntervalType.NONE:
            raise forms.ValidationError(
                "A Lower/Upper Interval Type must be selected when a value is given for the Lower or Upper interval."
            )
        return data

    @property
    def helper(self):
        for fld in ["comments"]:
            self.fields[fld].widget.attrs["rows"] = 3
        helper = BaseFormHelper(
            self,
            help_text="The exposure levels entered in this subform will be linked to a specific result below. If exposure levels are reported separately for sub-populations (e.g., exposed and unexposed) and results are also reported separately, create a separate entry for each sub-population. If exposure levels are reported separately but results are reported for the full population, only one entry will be linked to the result, so information on the remaining sub-group may be captured in the comment field.",
        )
        helper.form_tag = False
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
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        for fld in ["description", "comments"]:
            self.fields[fld].widget.attrs["rows"] = 3
        helper.add_row("name", 3, "col-md-4")
        helper.form_tag = False
        return helper


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = models.Outcome
        exclude = ("design",)
        widgets = {
            "endpoint": selectable.AutoCompleteWidget(
                lookup_class=lookups.EndpointLookup, allow_new=True
            ),
            "effect": selectable.AutoCompleteWidget(
                lookup_class=lookups.EffectLookup, allow_new=True
            ),
            "effect_detail": selectable.AutoCompleteWidget(
                lookup_class=lookups.EffectDetailLookup, allow_new=True
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        self.fields["comments"].widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
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
            "units": selectable.AutoCompleteWidget(
                lookup_class=lookups.DataExtractionUnitsLookup, allow_new=True
            ),
        }

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design
        self.fields["outcome"].queryset = self.instance.design.outcomes.all()
        self.fields["exposure_level"].queryset = self.instance.design.exposure_levels.all()
        self.fields["factors"].queryset = self.instance.design.adjustment_factors.all()

    def clean_variance_type(self):
        data = self.cleaned_data["variance_type"]
        variance = self.cleaned_data.get("variance")
        if variance and data == constants.VarianceType.NONE:
            raise forms.ValidationError(
                "A Variance Type must be selected when a value is given for Variance."
            )
        return data

    def clean_ci_type(self):
        data = self.cleaned_data["ci_type"]
        upper = self.cleaned_data.get("ci_ucl")
        lower = self.cleaned_data.get("ci_lcl")
        if (upper or lower) and data == constants.ConfidenceIntervalType.NONE:
            raise forms.ValidationError(
                "A Lower/Upper Bound Type must be selected when a value is given for the Lower or Upper bound."
            )
        return data

    @property
    def helper(self):
        for fld in ["effect_description", "statistical_method", "comments"]:
            self.fields[fld].widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
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
