from functools import partial

from crispy_forms import layout as cfl
from django import forms
from django.db.models import Q
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.urls import reverse

from ..assessment.autocomplete import DSSToxAutocomplete, EffectTagAutocomplete
from ..assessment.lookups import BaseEndpointLookup
from ..assessment.models import DoseUnits
from ..common import selectable
from ..common.autocomplete import (
    AutocompleteMultipleChoiceField,
    AutocompleteSelectMultipleWidget,
    AutocompleteSelectWidget,
)
from ..common.forms import (
    ASSESSMENT_UNIQUE_MESSAGE,
    BaseFormHelper,
    CopyAsNewSelectorFormV2,
    form_actions_apply_filters,
    form_actions_create_or_close,
)
from ..common.helper import tryParseInt
from ..study.autocomplete import StudyAutocomplete
from . import autocomplete, constants, lookups, models


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
        self.fields["description"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.CriteriaLookup, allow_new=True
        )
        self.instance.assessment = assessment
        self.fields["description"].widget.update_query_parameters(
            {"related": self.instance.assessment_id}
        )

    def clean(self):
        super().clean()
        # assessment-description unique-together constraint check must be
        # added since assessment is not included on form
        pk = getattr(self.instance, "pk", None)
        crits = models.Criteria.objects.filter(
            assessment=self.instance.assessment,
            description=self.cleaned_data.get("description", ""),
        ).exclude(pk=pk)

        if crits.count() > 0:
            self.add_error("description", ASSESSMENT_UNIQUE_MESSAGE)

        return self.cleaned_data

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

    def __init__(self, *args, **kwargs):
        study = kwargs.pop("parent", None)
        super().__init__(*args, **kwargs)
        self.fields["countries"].required = True
        self.fields["comments"] = self.fields.pop("comments")  # move to end
        self.fields["region"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.RegionLookup, allow_new=True
        )
        self.fields["state"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.StateLookup, allow_new=True
        )
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


class StudyPopulationSelectorForm(CopyAsNewSelectorFormV2):
    label = "Study Population"
    parent_field = "study_id"
    autocomplete_class = autocomplete.StudyPopulationAutocomplete


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
        self.fields["description"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.AdjustmentFactorLookup, allow_new=True
        )
        self.instance.assessment = assessment
        self.fields["description"].widget.update_query_parameters(
            {"related": self.instance.assessment_id}
        )

    def clean(self):
        super().clean()
        # assessment-description unique-together constraint check must be
        # added since assessment is not included on form
        pk = getattr(self.instance, "pk", None)
        crits = models.AdjustmentFactor.objects.filter(
            assessment=self.instance.assessment,
            description=self.cleaned_data.get("description", ""),
        ).exclude(pk=pk)

        if crits.count() > 0:
            self.add_error("description", ASSESSMENT_UNIQUE_MESSAGE)

        return self.cleaned_data

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

        self.fields["measured"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.ExposureMeasuredLookup, allow_new=True
        )
        self.fields["metric"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.ExposureMetricLookup, allow_new=True
        )
        self.fields["age_of_exposure"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.AgeOfExposureLookup, allow_new=True
        )

        if study_population:
            self.instance.study_population = study_population

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

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

        helper.add_row("name", 2, "col-md-6")
        helper.add_row("inhalation", 6, "col-md-2")
        helper.add_row("measured", 3, "col-md-4")
        helper.add_row("metric_description", 3, "col-md-4")
        helper.add_row("age_of_exposure", 3, "col-md-6")

        inhalation_idx = helper.find_layout_idx_for_field_name("inhalation")
        helper.layout[inhalation_idx].append(
            cfl.HTML(
                f"""<div class="col-md-12 pb-2">
                    <small class="form-text text-muted">{self.instance.ROUTE_HELP_TEXT}</small>
                </div>"""
            )
        )

        helper.add_create_btn("dtxsid", reverse("assessment:dtxsid_create"), "Add new DTXSID")
        url = reverse(
            "assessment:dose_units_create",
            args=(self.instance.study_population.study.assessment_id,),
        )
        helper.add_create_btn("metric_units", url, "Create units")
        helper.form_id = "exposure-form"
        return helper


class ExposureSelectorForm(CopyAsNewSelectorFormV2):
    label = "Exposure"
    parent_field = "study_population_id"
    autocomplete_class = autocomplete.ExposureAutocomplete


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
        self.fields["name"].widget = selectable.AutoCompleteWidget(
            lookup_class=BaseEndpointLookup, allow_new=True
        )
        self.fields["system"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.SystemLookup, allow_new=True
        )
        self.fields["effect"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EffectLookup, allow_new=True
        )
        self.fields["effect_subtype"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EffectSubtypeLookup, allow_new=True
        )
        self.fields["age_of_measurement"].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.AgeOfMeasurementLookup, allow_new=True
        )
        if assessment:
            self.instance.assessment = assessment
        if study_population:
            self.instance.study_population = study_population

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

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

        helper.add_row("name", 2, "col-md-6")
        helper.add_row("system", 3, "col-md-4")
        helper.add_row("diagnostic", 2, "col-md-6")
        helper.add_row("outcome_n", 2, "col-md-6")

        url = reverse("assessment:effect_tag_create", kwargs={"pk": self.instance.assessment.pk})
        helper.add_create_btn("effects", url, "Create effect tag")

        return helper


class OutcomeFilterForm(forms.Form):

    ORDER_BY_CHOICES = (
        ("study_population__study__short_citation", "study"),
        ("study_population__name", "study population"),
        ("name", "outcome name"),
        ("system", "system"),
        ("effect", "effect"),
        ("diagnostic", "diagnostic"),
    )

    studies = AutocompleteMultipleChoiceField(
        autocomplete_class=StudyAutocomplete,
        label="Study reference",
        help_text="ex: Smith et al. 2010",
        required=False,
    )

    name = forms.CharField(
        label="Outcome name",
        widget=selectable.AutoCompleteWidget(lookups.OutcomeLookup),
        help_text="ex: blood, glucose",
        required=False,
    )

    study_population = forms.CharField(
        label="Study population",
        widget=selectable.AutoCompleteWidget(lookups.StudyPopulationByAssessmentLookup),
        help_text="ex: population near a Teflon manufacturing plant",
        required=False,
    )

    metric = forms.CharField(
        label="Measurement metric",
        widget=selectable.AutoCompleteWidget(lookups.RelatedExposureMetricLookup),
        help_text="ex: drinking water",
        required=False,
    )

    age_profile = forms.CharField(
        label="Age profile",
        widget=selectable.AutoCompleteWidget(lookups.RelatedStudyPopulationAgeProfileLookup),
        help_text="ex: children",
        required=False,
    )

    source = forms.CharField(
        label="Study population source",
        widget=selectable.AutoCompleteWidget(lookups.RelatedStudyPopulationSourceLookup),
        help_text="ex: occupational exposure",
        required=False,
    )

    country = forms.CharField(
        label="Study population country",
        widget=selectable.AutoCompleteWidget(lookups.RelatedCountryNameLookup),
        help_text="ex: Japan",
        required=False,
    )

    design = forms.MultipleChoiceField(
        label="Study design",
        choices=constants.Design.choices,
        widget=forms.CheckboxSelectMultiple,
        initial=constants.Design.values,
        required=False,
    )

    system = forms.CharField(
        label="System",
        widget=selectable.AutoCompleteWidget(lookups.RelatedSystemLookup),
        help_text="ex: immune and lymphatic system",
        required=False,
    )

    effect = forms.CharField(
        label="Effect",
        widget=selectable.AutoCompleteWidget(lookups.RelatedEffectLookup),
        help_text="ex: Cancer",
        required=False,
    )

    effect_subtype = forms.CharField(
        label="Effect subtype",
        widget=selectable.AutoCompleteWidget(lookups.RelatedEffectSubtypeLookup),
        help_text="ex: Melanoma",
        required=False,
    )

    diagnostic = forms.MultipleChoiceField(
        choices=constants.Diagnostic.choices,
        widget=forms.CheckboxSelectMultiple,
        initial=constants.Diagnostic.values,
        required=False,
    )

    metric_units = forms.ModelChoiceField(queryset=DoseUnits.objects.all(), required=False)
    order_by = forms.ChoiceField(
        choices=ORDER_BY_CHOICES,
    )
    paginate_by = forms.IntegerField(
        label="Items per page", min_value=10, initial=25, max_value=500, required=False
    )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop("assessment")
        super().__init__(*args, **kwargs)
        self.fields["studies"].set_filters({"assessment_id": assessment.id, "epi": True})
        self.fields["metric_units"].queryset = DoseUnits.objects.get_epi_units(assessment.id)
        for field in self.fields:
            if field not in (
                "studies",
                "design",
                "diagnostic",
                "metric_units",
                "order_by",
                "paginate_by",
            ):
                self.fields[field].widget.update_query_parameters({"related": assessment.id})

    @property
    def helper(self):
        helper = BaseFormHelper(self, form_actions=form_actions_apply_filters())

        helper.form_method = "GET"

        helper.add_row("studies", 4, "col-md-3")
        helper.add_row("age_profile", 4, "col-md-3")
        helper.add_row("system", 4, "col-md-3")
        helper.add_row("metric_units", 3, "col-md-3")

        return helper

    def get_query(self):

        studies = self.cleaned_data.get("studies")
        name = self.cleaned_data.get("name")
        study_population = self.cleaned_data.get("study_population")
        metric = self.cleaned_data.get("metric")
        age_profile = self.cleaned_data.get("age_profile")
        source = self.cleaned_data.get("source")
        country = self.cleaned_data.get("country")
        design = self.cleaned_data.get("design")
        system = self.cleaned_data.get("system")
        effect = self.cleaned_data.get("effect")
        effect_subtype = self.cleaned_data.get("effect_subtype")
        diagnostic = self.cleaned_data.get("diagnostic")
        metric_units = self.cleaned_data.get("metric_units")

        query = Q()
        if studies:
            query &= Q(study_population__study__in=studies)
        if name:
            query &= Q(name__icontains=name)
        if study_population:
            query &= Q(study_population__name__icontains=study_population)
        if metric:
            query &= Q(study_population__exposures__metric__icontains=metric)
        if age_profile:
            query &= Q(study_population__age_profile__icontains=age_profile)
        if source:
            query &= Q(study_population__source__icontains=source)
        if country:
            query &= Q(study_population__countries__name__icontains=country)
        if design:
            query &= Q(study_population__design__in=design)
        if system:
            query &= Q(system__icontains=system)
        if effect:
            query &= Q(effect__icontains=effect)
        if effect_subtype:
            query &= Q(effect_subtype__icontains=effect_subtype)
        if diagnostic:
            query &= Q(diagnostic__in=diagnostic)
        if metric_units:
            query &= Q(study_population__exposures__metric_units=metric_units)
        return query

    def get_order_by(self):
        return self.cleaned_data.get("order_by", self.ORDER_BY_CHOICES[0][0])


class OutcomeSelectorForm(CopyAsNewSelectorFormV2):
    label = "Outcome"
    parent_field = "study_population_id"
    autocomplete_class = autocomplete.OutcomeAutocomplete


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
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

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

        return helper


class ComparisonSetByStudyPopulationSelectorForm(CopyAsNewSelectorFormV2):
    label = "Comparison set"
    parent_field = "study_population_id"
    autocomplete_class = autocomplete.ComparisonSetAutocomplete


class ComparisonSetByOutcomeSelectorForm(CopyAsNewSelectorFormV2):
    label = "Comparison set"
    parent_field = "outcome_id"
    autocomplete_class = autocomplete.ComparisonSetAutocomplete


class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        exclude = ("comparison_set", "group_id")


class SingleGroupForm(GroupForm):

    HELP_TEXT_UPDATE = "Update an existing group and numerical group descriptions."

    @property
    def helper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

        inputs = {
            "legend_text": f"Update {self.instance}",
            "help_text": self.HELP_TEXT_UPDATE,
            "cancel_url": self.instance.get_absolute_url(),
        }

        helper = BaseFormHelper(self, **inputs)

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
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) == forms.Textarea:
                widget.attrs["rows"] = 3

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


class ResultSelectorForm(CopyAsNewSelectorFormV2):
    label = "Result"
    parent_field = "outcome_id"
    autocomplete_class = autocomplete.ResultAutocomplete


class ResultUpdateForm(ResultForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comparison_set"].widget.attrs["disabled"] = True


class GroupResultForm(forms.ModelForm):
    class Meta:
        model = models.GroupResult
        exclude = ("result",)

    def __init__(self, *args, **kwargs):
        study_population = kwargs.pop("study_population", None)
        outcome = kwargs.pop("outcome", None)
        result = kwargs.pop("result", None)
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = models.Group.objects.filter(
            Q(comparison_set__study_population=study_population)
            | Q(comparison_set__outcome=outcome)
        )
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
