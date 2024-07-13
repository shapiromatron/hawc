from functools import partial

from crispy_forms import layout as cfl
from django import forms
from django.db.models import Q
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.urls import reverse

from ..assessment.autocomplete import DSSToxAutocomplete, EffectTagAutocomplete
from ..common.autocomplete import (
    AutocompleteMultipleChoiceField,
    AutocompleteSelectMultipleWidget,
    AutocompleteSelectWidget,
    AutocompleteTextWidget,
)
from ..common.forms import (
    BaseFormHelper,
    CopyForm,
    check_unique_for_assessment,
    form_actions_create_or_close,
)
from ..common.helper import tryParseInt
from . import autocomplete, models


class CriteriaForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study criteria"

    CREATE_HELP_TEXT = """
        Create a epidemiology study criteria. Study criteria can be applied to
        study populations as inclusion criteria, exclusion criteria, or
        confounding criteria. They are assessment-specific. Please take care
        not to duplicate existing factors."""

    class Meta:
        model = models.Criteria
        exclude = ("assessment",)

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.instance.assessment = assessment
        self.fields["description"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.CriteriaAutocomplete,
            field="description",
            filters={"assessment_id": assessment.id},
        )

    def clean_description(self):
        return check_unique_for_assessment(self, "description")

    @property
    def helper(self):
        return BaseFormHelper(
            self,
            legend_text=self.CREATE_LEGEND,
            help_text=self.CREATE_HELP_TEXT,
            form_actions=form_actions_create_or_close(),
        )


class StudyPopulationForm(forms.ModelForm):
    CREATE_LEGEND = "Create new study-population"

    CREATE_HELP_TEXT = ""

    UPDATE_HELP_TEXT = "Update an existing study-population."

    CRITERION_FIELDS = [
        "inclusion_criteria",
        "exclusion_criteria",
        "confounding_criteria",
    ]

    CRITERION_TYPE_CW = {
        "inclusion_criteria": "I",
        "exclusion_criteria": "E",
        "confounding_criteria": "C",
    }

    inclusion_criteria = AutocompleteMultipleChoiceField(
        autocomplete_class=autocomplete.CriteriaAutocomplete, required=False
    )

    exclusion_criteria = AutocompleteMultipleChoiceField(
        autocomplete_class=autocomplete.CriteriaAutocomplete, required=False
    )

    confounding_criteria = AutocompleteMultipleChoiceField(
        autocomplete_class=autocomplete.CriteriaAutocomplete, required=False
    )

    class Meta:
        model = models.StudyPopulation
        exclude = ("study", "criteria")
        labels = {"comments": "Recruitment description"}
        widgets = {
            "region": AutocompleteTextWidget(
                autocomplete_class=autocomplete.StudyPopulationAutocomplete, field="region"
            ),
            "state": AutocompleteTextWidget(
                autocomplete_class=autocomplete.StudyPopulationAutocomplete, field="state"
            ),
            "countries": AutocompleteSelectMultipleWidget(
                autocomplete_class=autocomplete.CountryAutocomplete
            ),
        }

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.fields["countries"].required = True
        self.fields["comments"] = self.fields.pop("comments")  # move to end
        if study:
            self.instance.study = study

        for fld in self.CRITERION_FIELDS:
            self.fields[fld].set_filters({"assessment_id": self.instance.study.assessment_id})
            if self.instance.id:
                self.fields[fld].initial = getattr(self.instance, fld)

            # set the help text here for the correct criteria field
            self.fields[fld].help_text = self.instance.CRITERIA_HELP_TEXTS.get(fld, "")

    def save_criteria(self):
        """
        StudyPopulationCriteria is a through model; requires the criteria type.
        We save the m2m relations using the additional information from the
        field-name
        """
        self.instance.spcriteria.all().delete()
        objs = []
        for field in self.CRITERION_FIELDS:
            for criteria in self.cleaned_data.get(field, []):
                objs.append(
                    models.StudyPopulationCriteria(
                        criteria=criteria,
                        study_population=self.instance,
                        criteria_type=self.CRITERION_TYPE_CW[field],
                    )
                )
        models.StudyPopulationCriteria.objects.bulk_create(objs)

    def save(self, commit=True):
        instance = super().save(commit)
        if commit:
            self.save_criteria()
        return instance

    @property
    def helper(self):
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
        helper.set_textarea_height()
        helper.add_row("name", 2, "col-md-6")
        helper.add_row("age_profile", 2, "col-md-6")
        helper.add_row("countries", 3, "col-md-4")
        helper.add_row("eligible_n", 3, "col-md-4")
        helper.add_row("inclusion_criteria", 3, "col-md-4")

        url = reverse("epi:studycriteria_create", kwargs={"pk": self.instance.study.assessment.pk})

        helper.add_create_btn("inclusion_criteria", url, "Create criteria")
        helper.add_create_btn("exclusion_criteria", url, "Create criteria")
        helper.add_create_btn("confounding_criteria", url, "Create criteria")

        return helper

    def clean(self):
        cleaned_data = super().clean()
        countries = cleaned_data.get("countries")
        if not countries:
            self.add_error("countries", "At least one country must be selected")
        return cleaned_data


class StudyPopulationSelectorForm(CopyForm):
    legend_text = "Copy Study Population"
    help_text = "Select an existing study population as a template to create a new one."
    create_url_pattern = "epi:sp_create"
    selector = forms.ModelChoiceField(
        queryset=models.StudyPopulation.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            study=self.parent
        )


class AdjustmentFactorForm(forms.ModelForm):
    CREATE_LEGEND = "Create new adjustment factor"

    CREATE_HELP_TEXT = """
        Create a new adjustment factor. Adjustment factors can be applied to
        outcomes as applied or considered factors.
        They are assessment-specific.
        Please take care not to duplicate existing factors."""

    class Meta:
        model = models.AdjustmentFactor
        exclude = ("assessment",)

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.instance.assessment = assessment
        self.fields["description"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.AdjustmentFactorAutocomplete,
            field="description",
            filters={"assessment_id": assessment.id},
        )

    def clean_description(self):
        return check_unique_for_assessment(self, "description")

    @property
    def helper(self):
        return BaseFormHelper(
            self,
            legend_text=self.CREATE_LEGEND,
            help_text=self.CREATE_HELP_TEXT,
            form_actions=form_actions_create_or_close(),
        )


class ExposureForm(forms.ModelForm):
    HELP_TEXT_CREATE = """Create a new exposure."""
    HELP_TEXT_UPDATE = """Update an existing exposure."""

    class Meta:
        model = models.Exposure
        exclude = ("study_population",)
        widgets = {"dtxsid": AutocompleteSelectWidget(autocomplete_class=DSSToxAutocomplete)}

    def __init__(self, *args, **kwargs):
        study_population = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)

        self.fields["measured"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExposureAutocomplete, field="measured"
        )
        self.fields["metric"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExposureAutocomplete, field="metric"
        )
        self.fields["age_of_exposure"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.ExposureAutocomplete, field="age_of_exposure"
        )

        if study_population:
            self.instance.study_population = study_population

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new exposure",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study_population.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        helper.add_row("name", 2, "col-md-6")
        helper.add_row("inhalation", 6, "col-md-2")
        helper.add_row("measured", 3, "col-md-4")
        helper.add_row("metric_description", 3, "col-md-4")
        helper.add_row("age_of_exposure", 3, "col-md-6")

        inhalation_idx = helper.find_layout_idx_for_field_name("inhalation")
        helper.layout[inhalation_idx].css_class = "px-3"
        helper.layout.insert(
            inhalation_idx,
            cfl.HTML(
                f"""<div class="form-group mb-2">
                <p><b>Exposure Route(s)</b></p>
                <p class="text-muted">{self.instance.ROUTE_HELP_TEXT}</p></div>"""
            ),
        )

        helper.add_create_btn("dtxsid", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        url = reverse(
            "assessment:dose_units_create",
            args=(self.instance.study_population.study.assessment_id,),
        )
        helper.add_create_btn("metric_units", url, "Create units")
        helper.form_id = "exposure-form"
        return helper


class ExposureSelectorForm(CopyForm):
    legend_text = "Copy Exposure"
    help_text = "Select an existing exposure as a template to create a new one."
    create_url_pattern = "epi:exp_create"
    selector = forms.ModelChoiceField(
        queryset=models.Exposure.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            study_population=self.parent
        )


class OutcomeForm(forms.ModelForm):
    HELP_TEXT_CREATE = """Create a new outcome. An
        outcome is an response measured in an epidemiological study,
        associated with an exposure-metric. The overall outcome is
        described, and then quantitative differences in response based on
        different exposure-metric groups is detailed below.
    """
    HELP_TEXT_UPDATE = """Update an existing outcome."""

    class Meta:
        model = models.Outcome
        exclude = ("assessment", "study_population")
        labels = {"summary": "Comments"}
        widgets = {
            "effects": AutocompleteSelectMultipleWidget(autocomplete_class=EffectTagAutocomplete)
        }

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("assessment", None)
        study_population = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.fields["name"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete, field="name"
        )
        self.fields["system"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete, field="system"
        )
        self.fields["effect"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete, field="effect"
        )
        self.fields["effect_subtype"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete, field="effect_subtype"
        )
        self.fields["age_of_measurement"].widget = AutocompleteTextWidget(
            autocomplete_class=autocomplete.OutcomeAutocomplete, field="age_of_measurement"
        )
        if assessment:
            self.instance.assessment = assessment
        if study_population:
            self.instance.study_population = study_population

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new outcome",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study_population.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        helper.add_row("name", 2, "col-md-6")
        helper.add_row("system", 3, "col-md-4")
        helper.add_row("diagnostic", 2, "col-md-6")
        helper.add_row("outcome_n", 2, "col-md-6")

        url = reverse("assessment:effect_tag_create", kwargs={"pk": self.instance.assessment.pk})
        helper.add_create_btn("effects", url, "Create effect tag")

        return helper


class OutcomeSelectorForm(CopyForm):
    legend_text = "Copy Outcome"
    help_text = "Select an existing outcome as a template to create a new one."
    create_url_pattern = "epi:outcome_create"
    selector = forms.ModelChoiceField(
        queryset=models.Outcome.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            study_population=self.parent
        )


class ComparisonSet(forms.ModelForm):
    HELP_TEXT_CREATE = ""
    HELP_TEXT_UPDATE = """Update an existing comparison set."""

    class Meta:
        model = models.ComparisonSet
        exclude = ("study_population", "outcome")

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        if self.parent:
            if type(self.parent) == models.StudyPopulation:
                self.instance.study_population = self.parent
            elif type(self.parent) == models.Outcome:
                self.instance.outcome = self.parent

        filters = {}
        if self.instance.study_population:
            filters["study_population"] = self.instance.study_population
        else:
            filters["study_population"] = self.instance.outcome.study_population
        self.fields["exposure"].queryset = self.fields["exposure"].queryset.filter(**filters)

    @property
    def helper(self):
        if self.instance.id:
            if self.instance.outcome:
                url = self.instance.outcome.get_absolute_url()
            else:
                url = self.instance.study_population.get_absolute_url()
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": url,
            }
        else:
            inputs = {
                "legend_text": "Create new comparison set",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.parent.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        return helper


class ComparisonSetByStudyPopulationSelectorForm(CopyForm):
    legend_text = "Copy Comparison Set"
    help_text = "Select an existing comparison set as a template to create a new one."
    create_url_pattern = "epi:cs_create"
    selector = forms.ModelChoiceField(
        queryset=models.ComparisonSet.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            study_population=self.parent
        )


class ComparisonSetByOutcomeSelectorForm(CopyForm):
    legend_text = "Copy Comparison Set"
    help_text = "Select an existing comparison set as a template to create a new one."
    create_url_pattern = "epi:cs_outcome_create"
    selector = forms.ModelChoiceField(
        queryset=models.ComparisonSet.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            outcome=self.parent
        )


class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        exclude = ("comparison_set", "group_id")


class SingleGroupForm(GroupForm):
    HELP_TEXT_UPDATE = "Update an existing group and numerical group descriptions."

    @property
    def helper(self):
        inputs = {
            "legend_text": f"Update {self.instance}",
            "help_text": self.HELP_TEXT_UPDATE,
            "cancel_url": self.instance.get_absolute_url(),
        }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        helper.add_row("name", 3, "col-md-4")
        helper.add_row("sex", 2, "col-md-6")
        helper.add_row("eligible_n", 3, "col-md-4")
        return helper


class BaseGroupFormset(BaseModelFormSet):
    def clean(self):
        super().clean()

        # check that there is at least one exposure-group
        count = len([f for f in self.forms if f.is_valid() and f.clean()])
        if count < 1:
            raise forms.ValidationError("At least one group is required.")


GroupFormset = modelformset_factory(
    models.Group, form=GroupForm, formset=BaseGroupFormset, can_delete=True, extra=0
)


BlankGroupFormset = modelformset_factory(
    models.Group, form=GroupForm, formset=BaseGroupFormset, can_delete=False, extra=1
)


class CentralTendencyForm(forms.ModelForm):
    class Meta:
        model = models.CentralTendency
        exclude = ("exposure",)


class BaseCentralTendencyFormset(BaseModelFormSet):
    def clean(self):
        super().clean()

        # check that there is at least one exposure-group
        count = len([f for f in self.forms if f.is_valid() and f.clean()])
        if count < 1:
            raise forms.ValidationError("At least one central tendency is required.")


CentralTendencyFormset = modelformset_factory(
    models.CentralTendency,
    form=CentralTendencyForm,
    formset=BaseCentralTendencyFormset,
    can_delete=True,
    extra=0,
)


BlankCentralTendencyFormset = modelformset_factory(
    models.CentralTendency,
    form=CentralTendencyForm,
    formset=BaseCentralTendencyFormset,
    can_delete=False,
    extra=1,
)


class GroupNumericalDescriptionsForm(forms.ModelForm):
    class Meta:
        model = models.GroupNumericalDescriptions
        exclude = ("group",)


class BaseGroupNumericalDescriptionsFormset(BaseModelFormSet):
    pass


GroupNumericalDescriptionsFormset = modelformset_factory(
    models.GroupNumericalDescriptions,
    form=GroupNumericalDescriptionsForm,
    formset=BaseGroupNumericalDescriptionsFormset,
    can_delete=True,
    extra=1,
)


class ResultForm(forms.ModelForm):
    HELP_TEXT_CREATE = """Describe results found for measured outcome."""
    HELP_TEXT_UPDATE = """Update results found for measured outcome."""
    ADJUSTMENT_FIELDS = ["factors_applied", "factors_considered"]

    factors_applied = AutocompleteMultipleChoiceField(
        autocomplete_class=autocomplete.AdjustmentFactorAutocomplete,
        help_text="All adjustment factors included in final statistical model",
        required=False,
    )

    factors_considered = AutocompleteMultipleChoiceField(
        autocomplete_class=autocomplete.AdjustmentFactorAutocomplete,
        label="Adjustment factors considered",
        help_text=models.OPTIONAL_NOTE,
        required=False,
    )

    class Meta:
        model = models.Result
        exclude = ("outcome", "adjustment_factors")
        widgets = {
            "resulttags": AutocompleteSelectMultipleWidget(autocomplete_class=EffectTagAutocomplete)
        }

    def __init__(self, *args, **kwargs):
        outcome = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.fields["comments"] = self.fields.pop("comments")  # move to end

        if outcome:
            self.instance.outcome = outcome
        else:
            outcome = self.instance.outcome

        self.fields["comparison_set"].queryset = models.ComparisonSet.objects.filter(
            Q(study_population=outcome.study_population) | Q(outcome=outcome)
        )

        for fld in self.ADJUSTMENT_FIELDS:
            self.fields[fld].set_filters({"assessment_id": self.instance.outcome.assessment_id})
            if self.instance.id:
                self.fields[fld].initial = getattr(self.instance, fld)

    def save_factors(self):
        """
        Adjustment factors is a through model; requires the inclusion type.
        We save the m2m relations using the additional information from the
        field-name
        """
        self.instance.resfactors.all().delete()
        objs = []

        applied = self.cleaned_data.get("factors_applied", [])
        objs.extend(
            [
                models.ResultAdjustmentFactor(
                    adjustment_factor=af,
                    result=self.instance,
                    included_in_final_model=True,
                )
                for af in applied
            ]
        )

        considered = self.cleaned_data.get("factors_considered", [])
        considered = set(considered) - set(applied)
        objs.extend(
            [
                models.ResultAdjustmentFactor(
                    adjustment_factor=af,
                    result=self.instance,
                    included_in_final_model=False,
                )
                for af in considered
            ]
        )

        models.ResultAdjustmentFactor.objects.bulk_create(objs)

    def save(self, commit=True):
        instance = super().save(commit)
        if commit:
            self.save_factors()
        return instance

    @property
    def helper(self):
        if self.instance.id:
            inputs = {
                "legend_text": f"Update {self.instance}",
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url(),
            }
        else:
            inputs = {
                "legend_text": "Create new set of results",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.outcome.get_absolute_url(),
            }

        helper = BaseFormHelper(self, **inputs)
        helper.set_textarea_height()
        helper.add_row("name", 2, "col-md-6")
        helper.add_row("metric", 3, "col-md-4")
        helper.add_row("data_location", 2, "col-md-6")
        helper.add_row("dose_response", 3, "col-md-4")
        helper.add_row("statistical_power", 4, "col-md-3")
        helper.add_row("factors_applied", 2, "col-md-6")
        helper.add_row("estimate_type", 3, "col-md-4")
        helper.add_row("resulttags", 1, "col-md-6")

        url = reverse(
            "assessment:effect_tag_create",
            kwargs={"pk": self.instance.outcome.assessment_id},
        )
        helper.add_create_btn("resulttags", url, "Add new result tag")

        url = reverse(
            "epi:adjustmentfactor_create",
            kwargs={"pk": self.instance.outcome.assessment_id},
        )
        helper.add_create_btn("factors_applied", url, "Add new adjustment factor")
        helper.add_create_btn("factors_considered", url, "Add new adjustment factor")

        return helper


class ResultSelectorForm(CopyForm):
    legend_text = "Copy Result"
    help_text = "Select an existing result as a template to create a new one."
    create_url_pattern = "epi:result_create"
    selector = forms.ModelChoiceField(
        queryset=models.Result.objects.all(), empty_label=None, label="Select template"
    )

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.fields["selector"].queryset = self.fields["selector"].queryset.filter(
            outcome=self.parent
        )


class ResultUpdateForm(ResultForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comparison_set"].widget.attrs["disabled"] = True


class GroupSelectWidget(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # show the parent's name in case groups are named the same across comparison sets
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            option["label"] = f"{value.instance.comparison_set} - {value.instance.name}"
        return option


class GroupResultForm(forms.ModelForm):
    class Meta:
        model = models.GroupResult
        exclude = ("result",)
        widgets = {"group": GroupSelectWidget}

    def __init__(self, *args, **kwargs):
        study_population = kwargs.pop("study_population", None)
        outcome = kwargs.pop("outcome", None)
        result = kwargs.pop("result", None)
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = models.Group.objects.filter(
            Q(comparison_set__study_population=study_population)
            | Q(comparison_set__outcome=outcome)
        ).select_related("comparison_set")
        if result:
            self.instance.result = result

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if fld == "group":
                widget.attrs["class"] = "groupField"
                widget.attrs["style"] = "display: none;"
            if fld == "n":
                widget.attrs["class"] = "nField"

        helper = BaseFormHelper(self)
        helper.form_tag = False

        return helper


class BaseGroupResultFormset(BaseModelFormSet):
    def __init__(self, **kwargs):
        study_population = kwargs.pop("study_population", None)
        outcome = kwargs.pop("outcome", None)
        self.result = kwargs.pop("result", None)
        super().__init__(**kwargs)
        self.form = partial(
            self.form,
            study_population=study_population,
            outcome=outcome,
            result=self.result,
        )

    def clean(self):
        super().clean()

        # check that there is at least one result-group
        count = len([f for f in self.forms if f.is_valid() and f.clean()])
        if count < 1:
            raise forms.ValidationError("At least one group is required.")

        mfs = 0
        for form in self.forms:
            if form.cleaned_data["is_main_finding"]:
                mfs += 1

        if mfs > 1:
            raise forms.ValidationError("Only one-group can be the main-finding.")

        if self.result:
            comparison_set_id = self.result.comparison_set_id
        else:
            comparison_set_id = tryParseInt(self.data["comparison_set"], -1)

        # exit early if any individual form is invalid
        if any([not form.is_valid() for form in self.forms]):
            return

        # Ensure all groups in group collection are accounted for,
        # and no other groups exist
        group_ids = [form.cleaned_data["group"].id for form in self.forms]
        selectedGroups = models.Group.objects.filter(
            id__in=group_ids, comparison_set_id=comparison_set_id
        )
        allGroups = models.Group.objects.filter(comparison_set_id=comparison_set_id)
        if selectedGroups.count() != allGroups.count():
            raise forms.ValidationError("Missing group(s) in this comparison set")


GroupResultFormset = modelformset_factory(
    models.GroupResult,
    form=GroupResultForm,
    formset=BaseGroupResultFormset,
    can_delete=False,
    extra=0,
)


BlankGroupResultFormset = modelformset_factory(
    models.GroupResult,
    form=GroupResultForm,
    formset=BaseGroupResultFormset,
    can_delete=False,
    extra=1,
)
