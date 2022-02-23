from django import forms

from hawc.apps.common.forms import BaseFormHelper
from hawc.apps.epi import lookups

from ..assessment.lookups import DssToxIdLookup
from ..common import selectable
from . import models


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study-population"

    CREATE_HELP_TEXT = ""

    UPDATE_HELP_TEXT = "Update an existing study-population."

    # TODO: fix country lookup
    countries = selectable.AutoCompleteSelectMultipleField(
        lookups.RelatedCountryNameLookup, required=False
    )

    class Meta:
        model = models.Design
        exclude = ("study",)
        labels = {}

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if study:
            self.instance.study = study

    @property
    def helper(self):
        text_area_flds = ["age_profile"]
        for fld in text_area_flds:
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

        helper.add_row("study_design", 3, "col-md-4")
        helper.add_row("age_description", 3, "col-md-4")
        helper.add_row("summary", 2, "col-md-6")
        helper.add_row("countries", 4, "col-md-3")

        return helper


class CriteriaForm(forms.ModelForm):
    class Meta:
        model = models.Criteria
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 1, "col-md-4")
        return helper


class ChemicalForm(forms.ModelForm):
    class Meta:
        model = models.Chemical
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

        self.fields["dsstox"].widget = selectable.AutoCompleteSelectWidget(
            lookup_class=DssToxIdLookup
        )

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 2, "col-md-4")
        return helper


class ExposureForm(forms.ModelForm):
    class Meta:
        model = models.Exposure
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        text_area_flds = ["measurement_type", "comments"]
        for fld in text_area_flds:
            self.fields[fld].widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 3, "col-md-3")
        helper.add_row("measurement_timing", 4, "col-md-3")
        return helper


class ExposureLevelForm(forms.ModelForm):
    class Meta:
        model = models.ExposureLevel
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        text_area_flds = ["comments"]
        for fld in text_area_flds:
            self.fields[fld].widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
        helper.form_tag = False
        helper.add_row("name", 4, "col-md-3")
        helper.add_row("central_tendency", 6, "col-md-2")
        helper.add_row("neg_exposure", 3, ["col-md-3", "col-md-4", "col-md-3"])
        return helper


class AdjustmentFactorForm(forms.ModelForm):
    class Meta:
        model = models.AdjustmentFactor
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.add_row("name", 2, "col-md-4")
        helper.form_tag = False
        return helper


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = models.Outcome
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        helper = BaseFormHelper(self)
        helper.add_row("name", 3, "col-md-4")
        helper.form_tag = False
        return helper


class DataExtractionForm(forms.ModelForm):
    class Meta:
        model = models.DataExtraction
        exclude = ("design",)
        labels = {}

    def __init__(self, *args, **kwargs):
        design = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if design:
            self.instance.design = design

    @property
    def helper(self):
        text_area_flds = ["comments"]
        for fld in text_area_flds:
            self.fields[fld].widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
        helper.add_row("sub_population", 5, "col-md-2")
        helper.add_row("effect_estimate_type", 3, "col-md-4")
        helper.add_row("exposure_rank", 6, "col-md-2")
        helper.add_row(
            "adjustment_factor", 5, ["col-md-2", "col-md-2", "col-md-2", "col-md-2", "col-md-4"]
        )
        helper.form_tag = False
        return helper
