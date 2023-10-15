from functools import partial

from django import forms
from django.forms.models import modelformset_factory
from django.urls import reverse

from ..common.autocomplete import AutocompleteSelectMultipleWidget, AutocompleteTextWidget
from ..common.forms import BaseFormHelper, CopyForm
from ..epi.autocomplete import AdjustmentFactorAutocomplete, CriteriaAutocomplete
from . import autocomplete, models


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

    CRITERION_FIELDS = ("inclusion_criteria", "exclusion_criteria")

    class Meta:
        model = models.MetaProtocol
        exclude = ("study",)
        widgets = {
            "lit_search_start_date": forms.DateInput(attrs={"type": "date"}),
            "lit_search_end_date": forms.DateInput(attrs={"type": "date"}),
            "inclusion_criteria": AutocompleteSelectMultipleWidget(
                autocomplete_class=CriteriaAutocomplete
            ),
            "exclusion_criteria": AutocompleteSelectMultipleWidget(
                autocomplete_class=CriteriaAutocomplete
            ),
        }

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if parent:
            self.instance.study = parent

        filters = {"assessment_id": self.instance.study.assessment_id}
        for field in self.CRITERION_FIELDS:
            self.fields[field].widget.set_filters(filters)

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
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

    class Meta:
        model = models.MetaResult
        exclude = ("protocol",)
        widgets = {
            "health_outcome": AutocompleteTextWidget(
                autocomplete_class=autocomplete.MetaResultAutocomplete, field="health_outcome"
            ),
            "exposure_name": AutocompleteTextWidget(
                autocomplete_class=autocomplete.MetaResultAutocomplete, field="exposure_name"
            ),
            "adjustment_factors": AutocompleteSelectMultipleWidget(
                autocomplete_class=AdjustmentFactorAutocomplete
            ),
        }

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super().__init__(*args, **kwargs)

        if parent:
            self.instance.protocol = parent

        self.fields["health_outcome"].widget.update_filters(
            {"protocol__study__assessment_id": assessment.id}
        )
        self.fields["exposure_name"].widget.update_filters(
            {"protocol__study__assessment_id": assessment.id}
        )
        self.fields["adjustment_factors"].widget.set_filters({"assessment_id": assessment.id})

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
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


class MetaResultSelectorForm(CopyForm):
    legend_text = "Copy Meta Result"
    help_text = "Select an existing result as a template to create a new one."
    create_url_pattern = "meta:result_create"
    selector = forms.ModelChoiceField(
        queryset=models.MetaResult.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            protocol=self.parent
        )
