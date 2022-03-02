from django import forms
from django.urls import reverse

from hawc.apps.common.forms import BaseFormHelper, form_actions_create_or_close
from hawc.apps.epi.lookups import RelatedCountryNameLookup

from ..assessment.lookups import DssToxIdLookup
from ..common import selectable
from . import models, lookups


class DesignForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study-population"

    CREATE_HELP_TEXT = ""

    UPDATE_HELP_TEXT = "Update an existing study-population."

    countries = selectable.AutoCompleteSelectMultipleField(RelatedCountryNameLookup, required=False)

    criteria = forms.ModelMultipleChoiceField(
        queryset=None, to_field_name="name", label="Inclusion/exclusion criteria", required=False,
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
        self.fields["criteria"].queryset = self.instance.criteria

    @property
    def helper(self):
        text_area_flds = ["age_profile", "comments"]
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
        helper.add_row("summary", 4, "col-md-3")
        helper.add_row("years", 3, "col-md-4")
        helper.add_create_btn(
            field_name="criteria", url=reverse("epiv2:criteria-create", kwargs={"pk": self.instance.id}), title="Add criteria"
        )

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
        helper = BaseFormHelper(self, form_actions=form_actions_create_or_close())
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
        helper.add_row("name", 2, "col-md-6")
        helper.add_create_btn("dsstox", reverse("assessment:dtxsid_create"), "Add new DTXSID")
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
        self.fields["measurement_type"].widget.attrs["onchange"] = "exposureFunction(this.value);"
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
        helper.add_row("median", 8, "col-md-2")
        helper.add_row("neg_exposure", 3, "col-md-4")
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
        helper.add_row("name", 2, "col-md-6")
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

        self.fields["endpoint"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.OutcomeByDesignLookup,
            allow_new=True,
            query_params={"related": self.instance.design.id},
        )
        self.fields["health_outcome"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.OutcomeByHealthOutcome,
            allow_new=True,
            query_params={"related": self.instance.design.id},
        )

    @property
    def helper(self):
        text_area_flds = ["comments"]
        for fld in text_area_flds:
            self.fields[fld].widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
        helper.add_row("endpoint", 4, "col-md-3")
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
        text_area_flds = ["comments", "statistical_method"]
        for fld in text_area_flds:
            self.fields[fld].widget.attrs["rows"] = 3
        helper = BaseFormHelper(self)
        helper.add_row("sub_population", 5, "col-auto")
        helper.add_row("effect_estimate_type", 3, "col-md-4")
        helper.add_row("ci_lcl", 6, "col-md-2")
        helper.add_row(
            "adjustment_factor", 5, ["col-md-2", "col-md-2", "col-md-2", "col-md-2", "col-md-4"]
        )
        helper.form_tag = False
        return helper
