from functools import partial

from crispy_forms import layout as cfl
from django import forms
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.urls import reverse

from ..common import selectable
from ..common.forms import BaseFormHelper, CopyAsNewSelectorForm
from ..epi.lookups import AdjustmentFactorLookup, CriteriaLookup
from ..study.lookups import EpimetaStudyLookup
from . import lookups, models


class MetaProtocolForm(forms.ModelForm):

    CREATE_LEGEND = "Create a new meta-protocol"

    CREATE_HELP_TEXT = """
        Create a new meta-protocol for an epidemiological
        assessment. A meta-protocol contains the methodology behind a
        meta-analysis or pooled analysis, which are frequently used
        techniques used to quantitatively summarize results from
        multiple studies or reference populations.
    """

    UPDATE_HELP_TEXT = "Update an existing meta-protocol"

    inclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=CriteriaLookup, required=False
    )

    exclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=CriteriaLookup, required=False
    )

    CRITERION_FIELDS = [
        "inclusion_criteria",
        "exclusion_criteria",
    ]

    class Meta:
        model = models.MetaProtocol
        exclude = ("study",)

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if parent:
            self.instance.study = parent
        self.fields["inclusion_criteria"].widget.update_query_parameters(
            {"related": self.instance.study.assessment_id}
        )
        self.fields["exclusion_criteria"].widget.update_query_parameters(
            {"related": self.instance.study.assessment_id}
        )
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld in self.CRITERION_FIELDS:
                    widget.attrs["class"] = "col-md-10"
                else:
                    widget.attrs["class"] = "col-md-12"
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.UPDATE_HELP_TEXT,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text": self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.study.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)

        helper.add_row("name", 2, "col-md-6")
        helper.add_row("lit_search_strategy", 2, "col-md-6")
        helper.add_row("lit_search_start_date", 3, "col-md-4")
        helper.add_row("inclusion_criteria", 2, "col-md-6")

        url = reverse("epi:studycriteria_create", kwargs={"pk": self.instance.study.assessment.pk})
        helper.add_create_btn("inclusion_criteria", url, "Create criteria")
        helper.add_create_btn("exclusion_criteria", url, "Create criteria")

        return helper


class MetaResultForm(forms.ModelForm):

    CREATE_LEGEND = "Create a new meta-result"

    CREATE_HELP_TEXT = """
        Create a new meta-result for an epidemiological assessment.
        A meta-result is the aggregate result from a meta-analysis or
        pooled analysis from multiple primary literature components.
    """

    UPDATE_HELP_TEXT = "Update an existing meta-result"

    adjustment_factors = selectable.AutoCompleteSelectMultipleField(
        help_text="All factors which were included in final model",
        lookup_class=AdjustmentFactorLookup,
        required=False,
    )

    class Meta:
        model = models.MetaResult
        exclude = ("protocol",)

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super().__init__(*args, **kwargs)

        self.fields["health_outcome"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.MetaResultHealthOutcomeLookup, allow_new=True
        )

        self.fields["exposure_name"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.MetaResultExposureNameLookup, allow_new=True
        )

        if parent:
            self.instance.protocol = parent

        self.fields["adjustment_factors"].widget.update_query_parameters({"related": assessment.id})
        self.fields["health_outcome"].widget.update_query_parameters({"related": assessment.id})
        self.fields["exposure_name"].widget.update_query_parameters({"related": assessment.id})
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld == "adjustment_factors":
                    widget.attrs["class"] = "col-md-10"
                else:
                    widget.attrs["class"] = "col-md-12"
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.UPDATE_HELP_TEXT,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text": self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.protocol.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)

        helper.add_row("label", 2, "col-md-6")
        helper.add_row("health_outcome", 2, "col-md-6")
        helper.add_row("exposure_name", 2, "col-md-6")
        helper.add_row("number_studies", 3, "col-md-4")
        helper.add_row("n", 3, "col-md-4")
        helper.add_row("lower_ci", 3, "col-md-4")
        helper.add_row("adjustment_factors", 2, "col-md-6")

        url = reverse(
            "epi:adjustmentfactor_create",
            kwargs={"pk": self.instance.protocol.study.assessment.pk},
        )
        helper.add_create_btn("adjustment_factors", url, "Create criteria")

        return helper


class MetaResultFilterForm(forms.Form):

    ORDER_BY_CHOICES = (
        ("protocol__study__short_citation", "study"),
        ("label", "meta result label"),
        ("protocol__name", "protocol"),
        ("health_outcome", "health outcome"),
        ("exposure", "exposure"),
    )

    studies = selectable.AutoCompleteSelectMultipleField(
        label="Study reference",
        lookup_class=EpimetaStudyLookup,
        help_text="ex: Smith et al. 2010",
        required=False,
    )

    label = forms.CharField(
        label="Meta result label",
        widget=selectable.AutoCompleteWidget(lookups.MetaResultByAssessmentLookup),
        help_text="ex: ALL, folic acid, any time",
        required=False,
    )

    protocol = forms.CharField(
        label="Protocol",
        widget=selectable.AutoCompleteWidget(lookups.MetaProtocolLookup),
        help_text="ex: B vitamins and risk of cancer",
        required=False,
    )

    health_outcome = forms.CharField(
        label="Health outcome",
        widget=selectable.AutoCompleteWidget(lookups.MetaResultHealthOutcomeLookup),
        help_text="ex: Any adenoma",
        required=False,
    )

    exposure_name = forms.CharField(
        label="Exposure name",
        widget=selectable.AutoCompleteWidget(lookups.ExposureLookup),
        help_text="ex: Folate",
        required=False,
    )

    order_by = forms.ChoiceField(choices=ORDER_BY_CHOICES,)

    paginate_by = forms.IntegerField(
        label="Items per page", min_value=1, initial=25, max_value=10000, required=False
    )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ("order_by", "paginate_by"):
                self.fields[field].widget.update_query_parameters({"related": assessment.id})

    @property
    def helper(self):
        helper = BaseFormHelper(self, form_actions=[cfl.Submit("submit", "Apply filters")])
        helper.form_method = "GET"

        helper.add_row("studies", 4, "col-md-3")
        helper.add_row("exposure_name", 3, "col-md-3")

        return helper

    def get_query(self):

        studies = self.cleaned_data.get("studies")
        label = self.cleaned_data.get("label")
        protocol = self.cleaned_data.get("protocol")
        health_outcome = self.cleaned_data.get("health_outcome")
        exposure_name = self.cleaned_data.get("exposure_name")

        query = Q()
        if studies:
            query &= Q(protocol__study__in=studies)
        if label:
            query &= Q(label__icontains=label)
        if protocol:
            query &= Q(protocol__name__icontains=protocol)
        if health_outcome:
            query &= Q(health_outcome__icontains=health_outcome)
        if exposure_name:
            query &= Q(exposure_name__icontains=exposure_name)
        return query

    def get_order_by(self):
        return self.cleaned_data.get("order_by", self.ORDER_BY_CHOICES[0][0])


class SingleResultForm(forms.ModelForm):
    class Meta:
        model = models.SingleResult
        fields = (
            "study",
            "exposure_name",
            "weight",
            "n",
            "estimate",
            "lower_ci",
            "upper_ci",
            "ci_units",
            "notes",
        )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super().__init__(*args, **kwargs)

        if parent:
            self.instance.meta_result = parent

        self.fields["study"].queryset = self.fields["study"].queryset.filter(
            assessment=assessment, epi=True
        )

        self.helper = self.setHelper()

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs["class"] = "col-md-12"

            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

        self.fields["study"].widget.attrs["class"] += " studySearch"

        helper = BaseFormHelper(self)

        return helper


class BaseSingleResultFormset(forms.BaseModelFormSet):
    def __init__(self, **kwargs):
        assessment = kwargs.pop("assessment")
        super().__init__(**kwargs)
        self.form = partial(self.form, assessment=assessment)


SingleResultFormset = modelformset_factory(
    models.SingleResult,
    can_delete=True,
    form=SingleResultForm,
    formset=BaseSingleResultFormset,
    extra=1,
)


class MetaResultSelectorForm(CopyAsNewSelectorForm):
    label = "Meta Result"
    lookup_class = lookups.MetaResultByProtocolLookup
