from copy import copy

from django import forms
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.forms.widgets import CheckboxInput, TextInput
from collections import OrderedDict

from selectable import forms as selectable

from assessment.lookups import BaseEndpointLookup, EffectTagLookup
from utils.forms import FormsetWithIgnoredFields

from . import models, lookups


class StudyPopulationForm(forms.ModelForm):

    inclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.StudyCriteriaLookup,
        required=False)

    exclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.StudyCriteriaLookup,
        required=False)

    confounding_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.StudyCriteriaLookup,
        required=False)

    class Meta:
        fields = ('name',
                  'design',
                  'country',
                  'region',
                  'state',
                  'sex',
                  'ethnicity',
                  'fraction_male',
                  'fraction_male_calculated',
                  'n',
                  'starting_n',
                  'age_mean',
                  'age_mean_type',
                  'age_calculated',
                  'age_description',
                  'age_sd',
                  'age_sd_type',
                  'age_lower',
                  'age_lower_type',
                  'age_upper',
                  'age_upper_type',
                  'inclusion_criteria',
                  'exclusion_criteria',
                  'confounding_criteria')
        model = models.StudyPopulation
        exclude = ('study', )

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('parent', None)
        super(StudyPopulationForm, self).__init__(*args, **kwargs)
        self.fields['region'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.RegionLookup,
            allow_new=True)
        self.fields['state'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.StateLookup,
            allow_new=True)
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != CheckboxInput:
                widget.attrs['class'] = 'span12'
        if study:
            self.instance.study=study


class ExposureForm(forms.ModelForm):

    class Meta:
        model = models.Exposure
        exclude = ('study_population', )

    def __init__(self, *args, **kwargs):
        study_population = kwargs.pop('parent', None)
        super(ExposureForm, self).__init__(*args, **kwargs)
        if study_population:
            self.instance.study_population=study_population
        self.fields['exposure_form_definition'].widget = TextInput()
        for fld in self.fields.keys():
            f = self.fields[fld].widget
            if f.__class__ != CheckboxInput:
                f.attrs['class'] = 'span12'
        for fld in ('metric', 'metric_description', 'analytical_method',
                    'control_description'):
            self.fields[fld].widget.attrs['rows'] = 3


class ExposureGroupForm(forms.ModelForm):

    class Meta:
        fields = ('description',
                  'exposure_numeric',
                  'comparative_name',
                  'sex',
                  'ethnicity',
                  'fraction_male',
                  'fraction_male_calculated',
                  'n',
                  'starting_n',
                  'exposure_n',
                  'age_mean',
                  'age_mean_type',
                  'age_calculated',
                  'age_description',
                  'age_sd',
                  'age_sd_type',
                  'age_lower',
                  'age_lower_type',
                  'age_upper',
                  'age_upper_type')
        model = models.ExposureGroup

    def __init__(self, *args, **kwargs):
        super(ExposureGroupForm, self).__init__(*args, **kwargs)
        for key in ('exposure_numeric', 'fraction_male', 'fraction_male_calculated',
                    'n', 'starting_n', 'exposure_n', 'age_mean', 'age_mean_type',
                    'age_calculated', 'age_description', 'age_sd',
                    'age_sd_type', 'age_lower', 'age_lower_type', 'age_upper',
                    'age_upper_type'):
            self.fields[key].widget.attrs['class'] = 'input-small'

        for key in ('description', 'sex', 'comparative_name'):
            self.fields[key].widget.attrs['class'] = 'input-medium'


class BaseEGFormSet(BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        self.exposure = kwargs.pop('exposure', None)
        super(BaseEGFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        super(BaseEGFormSet, self).clean()
        # check that all descriptions are unique
        descriptions = []
        for form in self.forms:
            if form.is_valid() and form.clean():
                description = form.cleaned_data['description']
                if description in descriptions:
                    raise forms.ValidationError("Exposure-groups must have unique descriptions.")
                descriptions.append(description)

        # update new forms with  exposure_group_id, first get max ID
        max_exposure_group_id = -1
        for form in self.forms:
            if form.instance.exposure_group_id>max_exposure_group_id:
                max_exposure_group_id = form.instance.exposure_group_id

        # now increment
        for form in self.extra_forms:
            if form.is_valid() and form.clean():
                if self.exposure:
                    form.instance.exposure=self.exposure
                max_exposure_group_id += 1
                form.instance.exposure_group_id = max_exposure_group_id

        # check that there is at least one exposure-group
        count = len(filter(lambda f: f.is_valid() and f.clean(), self.forms))
        if count < 1:
            raise forms.ValidationError("At least one-exposure group is required.")

    def rebuild_exposure_group_id(self):
        # the exposure-group-id must start at zero and continue sequentially; this
        # method rebuilds the exposure-groups-ides in increasing order properly.
        # Note: cannot add into clean() because has_changed flag may not have been set.
        deleted_ids = sorted([form.instance.exposure_group_id for form in self.deleted_forms], reverse=True)
        for deleted_id in deleted_ids:
            for form in self.forms:
                if ((form not in self.deleted_forms) and (form.instance.exposure_group_id>deleted_id)):
                    form.instance.exposure_group_id -= 1
                    form.instance.save()


EGFormSet = modelformset_factory(
    models.ExposureGroup,
    form=ExposureGroupForm,
    formset=BaseEGFormSet,
    can_delete=True,
    extra=1)

BlankEGFormSet = modelformset_factory(
    models.ExposureGroup,
    form=ExposureGroupForm,
    formset=BaseEGFormSet,
    extra=1)


class FactorForm(forms.ModelForm):

    class Meta:
        model = models.Factor
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(FactorForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.FactorLookup,
            allow_new=True)
        self.instance.assessment = assessment
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span12'

    def clean(self):
        super(FactorForm, self).clean()
        # assessment-description unique-together constraint check must be
        # added since assessment is not included on form
        pk = getattr(self.instance, 'pk', None)
        crits = models.Factor.objects \
            .filter(assessment=self.instance.assessment,
                    description=self.cleaned_data.get('description', "")) \
            .exclude(pk=pk).values_list('pk', flat=True)

        if crits.count()>0:
            raise forms.ValidationError("Description must be unique for assessment.")

        return self.cleaned_data


class StudyCriteriaForm(forms.ModelForm):

    class Meta:
        model = models.StudyCriteria
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(StudyCriteriaForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.StudyCriteriaLookup,
            allow_new=True)
        self.instance.assessment = assessment
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span12'

    def clean(self):
        super(StudyCriteriaForm, self).clean()
        # assessment-description unique-together constraint check must be
        # added since assessment is not included on form
        pk = getattr(self.instance, 'pk', None)
        crits = models.StudyCriteria.objects \
            .filter(assessment=self.instance.assessment,
                    description=self.cleaned_data.get('description', "")) \
            .exclude(pk=pk).values_list('pk', flat=True)

        if crits.count()>0:
            raise forms.ValidationError("Description must be unique for assessment.")

        return self.cleaned_data


class AssessedOutcomeForm(forms.ModelForm):

    adjustment_factors = selectable.AutoCompleteSelectMultipleField(
        help_text="All factors which were included in final model",
        lookup_class=lookups.FactorLookup,
        required=False)

    confounders_considered = selectable.AutoCompleteSelectMultipleField(
        label="Adjustment factors considered",
        help_text="All factors which were examined (including those which were included in final model)",
        lookup_class=lookups.FactorLookup,
        required=False)

    effects = selectable.AutoCompleteSelectMultipleField(
        lookup_class=EffectTagLookup,
        required=False,
        help_text="Tags used to help categorize effect description.")

    class Meta:
        model = models.AssessedOutcome
        exclude = ('assessment', 'exposure')

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('assessment', None)
        exposure = kwargs.pop('parent', None)
        super(AssessedOutcomeForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = selectable.AutoCompleteWidget(
            lookup_class=BaseEndpointLookup,
            allow_new=True)
        if assessment:
            self.instance.assessment = assessment
        if exposure:
            self.instance.exposure = exposure
        self.fields['main_finding'].queryset = \
                self.fields['main_finding'].queryset.filter(
                        exposure=self.instance.exposure)
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span12'
        for fld in ('diagnostic_description', 'summary', 'prevalence_incidence',
                    'statistical_power_details', 'dose_response_details',
                    'statistical_metric_description'):
            self.fields[fld].widget.attrs['rows'] = 3


class AOGForm(forms.ModelForm):

    class Meta:
        fields = ('exposure_group', 'n', 'estimate', 'se', 'ci_units',
                  'lower_ci', 'upper_ci', 'p_value', 'p_value_qualifier')
        exclude = ('assessed_outcome', )
        model = models.AssessedOutcomeGroup

    def __init__(self, *args, **kwargs):
        super(AOGForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['exposure_group'].widget.attrs['readOnly'] = True
        self.fields['exposure_group'].widget.attrs['class'] = 'eg_fields'
        for key in ('n', 'estimate', 'se', 'ci_units', 'lower_ci',
                    'upper_ci', 'p_value', 'p_value_qualifier'):
            self.fields[key].widget.attrs['class'] = 'input-small'

    def clean_exposure_group(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.exposure_group
        else:
            return self.cleaned_data['exposure_group']


class BaseAOGFormSet(BaseModelFormSet):
    pass


AOGFormSet = modelformset_factory(
    models.AssessedOutcomeGroup,
    form=AOGForm,
    formset=BaseAOGFormSet,
    extra=0)


class MetaProtocolForm(forms.ModelForm):

    inclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.StudyCriteriaLookup,
        required=False)

    exclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.StudyCriteriaLookup,
        required=False)

    class Meta:
        model = models.MetaProtocol
        exclude = ('study', )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        super(MetaProtocolForm, self).__init__(*args, **kwargs)
        for fld in self.fields.keys():
            if fld in ('lit_search_notes', 'notes'):
                self.fields[fld].widget.attrs['rows'] = 3
            widget = self.fields[fld].widget
            if type(widget) != CheckboxInput:
                widget.attrs['class'] = 'span12'
        if parent:
            self.instance.study=parent


class MetaResultForm(forms.ModelForm):

    adjustment_factors = selectable.AutoCompleteSelectMultipleField(
        help_text="All factors which were included in final model",
        lookup_class=lookups.FactorLookup,
        required=False)

    class Meta:
        model = models.MetaResult
        exclude = ('protocol', )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        super(MetaResultForm, self).__init__(*args, **kwargs)

        self.fields['health_outcome'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.MetaResultHealthOutcomeLookup,
            allow_new=True)

        self.fields['exposure_name'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.MetaResultExposureNameLookup,
            allow_new=True)

        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if fld in ('health_outcome_notes', 'statistical_notes',
                       'notes', 'exposure_details'):
                self.fields[fld].widget.attrs['rows'] = 3
            if type(widget) != CheckboxInput:
                widget.attrs['class'] = 'span12'
        if parent:
            self.instance.protocol=parent


class SingleResultForm(forms.ModelForm):

    resultSelector = forms.ChoiceField(
        label="Results-data type",
        choices=((0, "Add new results"),
                 (1, "Use existing results")),
        initial=0)

    ao = selectable.AutoCompleteSelectField(
        lookup_class=lookups.AssessedOutcomeByStudyLookup,
        label='Assessed Outcome',
        required=False,
        widget=selectable.AutoComboboxSelectWidget)

    outcome_group = selectable.AutoCompleteSelectField(
        lookup_class=lookups.AssessedOutcomeGroupByAOLookup,
        label='Assessed Outcome Group',
        required=False,
        widget=selectable.AutoComboboxSelectWidget)

    class Meta:
        model = models.SingleResult
        fields = ('study', 'exposure_name', 'weight', 'outcome_group',
                  'n', 'estimate', 'lower_ci',
                  'upper_ci', 'ci_units', 'notes')

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super(SingleResultForm, self).__init__(*args, **kwargs)

        # re-order with custom-fields: https://djangosnippets.org/snippets/759/
        order = ('resultSelector', 'study', 'ao', 'outcome_group',
                 'exposure_name', 'weight', 'n',
                 'estimate', 'lower_ci', 'upper_ci', 'ci_units', 'notes')
        tmp = copy(self.fields)
        self.fields = OrderedDict()
        for item in order:
            self.fields[item] = tmp[item]

        def updateClasses(fields, cls):
            for fld in fields:
                self.fields[fld].widget.attrs["class"] = cls

        if assessment:
            # used with a single form; not used in formset_factory
            return forms.ModelChoiceField(
                queryset=self.fields["study"].queryset\
                             .filter(assessment=assessment, study_type=1))

        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if fld == "notes":
                widget.attrs['rows'] = 3

        updateClasses(("resultSelector", ), "unstyled singleResultType")
        updateClasses(("study", "exposure_name", "weight", "notes"), "span12")
        updateClasses(("ao", "outcome_group", ), "span11 isAOG")
        updateClasses(("n", "estimate", "lower_ci", "upper_ci", 'ci_units'), "span12 isntAOG")
        self.fields['study'].widget.attrs["class"] += " studySearch"
        self.fields['ao'].widget.attrs["class"]  += " aoSearch"
        self.fields['outcome_group'].widget.attrs["class"] += " aogSearch"

        if parent:
            self.instance.meta_result=parent

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        # todo: removed check, since can't specify instance in formset.
        #  Ideally would be able to check this.
        # if weight is None and self.instance.meta_result.protocol.protocol_type == 0:
        #     raise forms.ValidationError("For meta-analysis epidemiological protocols, the weight-field is required")
        return weight

    def clean(self):
        cleaned_data = super(SingleResultForm, self).clean()

        def anyNull(dict, fields):
            for field in fields:
                if dict.get(field) is None:
                    return True
            return False

        if int(cleaned_data.get('resultSelector')) == 0:
            if anyNull(cleaned_data, ('n', 'estimate', 'lower_ci', 'upper_ci')):
                raise forms.ValidationError("If manually entering single-study data, "
                                      "N, Risk estimate, and upper and lower CI are required.")
        else:
            if anyNull(cleaned_data, ('study', 'ao', 'outcome_group')):
                raise forms.ValidationError("If entering single-study data using an Assessed Outcome Group, "
                                      "Study, Assessed-Outcome, and Assessed-Outcome Group are required.")

        return cleaned_data


class EmptySingleResultFormset(FormsetWithIgnoredFields):
    ignored_fields = ['resultSelector']

    def get_queryset(self):
        return models.SingleResult.objects.none()


class LoadedSingleResultFormset(FormsetWithIgnoredFields):
    ignored_fields = ['resultSelector']


SingleResultFormset = modelformset_factory(
    models.SingleResult,
    can_delete=True,
    form=SingleResultForm,
    formset=LoadedSingleResultFormset,
    extra=1)


def meta_result_clean_update_formset(formset, assessment):
    # cleanup required to get the formset in usable-shape
    for form in formset.forms:
        form.fields['study'].queryset = form.fields['study'].queryset.filter(assessment=assessment, study_type=1)
        if form.instance and form.instance.outcome_group:
            form.initial['ao'] = form.instance.outcome_group.assessed_outcome.pk
            form.initial['resultSelector'] = 1


class StudyPopulationSelectorForm(forms.Form):

    selector = selectable.AutoCompleteSelectField(
        lookup_class=lookups.StudyPopulationByStudyLookup,
        label='Study Population',
        widget=selectable.AutoComboboxSelectWidget)

    def __init__(self, *args, **kwargs):
        super(StudyPopulationSelectorForm, self).__init__(*args, **kwargs)
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span11'


class ExposureSelectorForm(forms.Form):

    selector = selectable.AutoCompleteSelectField(
        lookup_class=lookups.ExposureByStudyLookup,
        label='Exposure',
        widget=selectable.AutoComboboxSelectWidget)

    def __init__(self, *args, **kwargs):
        super(ExposureSelectorForm, self).__init__(*args, **kwargs)
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span11'


class AssesedOutcomeSelectorForm(forms.Form):

    selector = selectable.AutoCompleteSelectField(
        lookup_class=lookups.AssessedOutcomeByStudyLookup,
        label='Assessed Outcome',
        widget=selectable.AutoComboboxSelectWidget)

    def __init__(self, *args, **kwargs):
        super(AssesedOutcomeSelectorForm, self).__init__(*args, **kwargs)
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span11'


class MetaResultSelectorForm(forms.Form):

    selector = selectable.AutoCompleteSelectField(
        lookup_class=lookups.MetaResultByStudyLookup,
        label='Meta Result',
        widget=selectable.AutoComboboxSelectWidget)

    def __init__(self, *args, **kwargs):
        super(MetaResultSelectorForm, self).__init__(*args, **kwargs)
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span11'
