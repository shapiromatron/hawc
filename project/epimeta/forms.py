from collections import OrderedDict
from copy import copy

from django import forms
from django.forms.models import modelformset_factory
from django.forms.widgets import CheckboxInput

from selectable import forms as selectable

from utils.forms import FormsetWithIgnoredFields, anyNull
from epi2.lookups import AdjustmentFactorLookup, CriteriaLookup

from . import models, lookups


class MetaProtocolForm(forms.ModelForm):

    inclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=CriteriaLookup,
        required=False)

    exclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=CriteriaLookup,
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
            self.instance.study = parent
        self.fields['inclusion_criteria'].widget.update_query_parameters(
            {'related': self.instance.study.assessment_id})
        self.fields['exclusion_criteria'].widget.update_query_parameters(
            {'related': self.instance.study.assessment_id})


class MetaResultForm(forms.ModelForm):

    adjustment_factors = selectable.AutoCompleteSelectMultipleField(
        help_text="All factors which were included in final model",
        lookup_class=AdjustmentFactorLookup,
        required=False)

    class Meta:
        model = models.MetaResult
        exclude = ('protocol', )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        assessment_id = kwargs.pop('assessment_id')
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
            self.instance.protocol = parent

        self.fields['adjustment_factors'].widget.update_query_parameters(
                {'related': assessment_id})
        self.fields['health_outcome'].widget.update_query_parameters(
                {'related': assessment_id})
        self.fields['exposure_name'].widget.update_query_parameters(
                {'related': assessment_id})


class SingleResultForm(forms.ModelForm):

    resultSelector = forms.ChoiceField(
        label="Results-data type",
        choices=((0, "Add new results"),
                 (1, "Use existing results")),
        initial=0)

    class Meta:
        model = models.SingleResult
        fields = ('study', 'exposure_name', 'weight',
                  'n', 'estimate', 'lower_ci',
                  'upper_ci', 'ci_units', 'notes')

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", None)
        assessment = kwargs.pop("assessment", None)
        super(SingleResultForm, self).__init__(*args, **kwargs)

        # re-order with custom-fields: https://djangosnippets.org/snippets/759/
        order = ('resultSelector', 'study', 'exposure_name',
                 'weight', 'n', 'estimate',
                 'lower_ci', 'upper_ci', 'ci_units',
                 'notes')
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
                queryset=self.fields["study"].queryset.filter(
                    assessment=assessment, study_type=1))

        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if fld == "notes":
                widget.attrs['rows'] = 3

        updateClasses(("resultSelector", ), "unstyled singleResultType")
        updateClasses(("study", "exposure_name", "weight", "notes"), "span12")
        updateClasses(("n", "estimate", "lower_ci", "upper_ci", 'ci_units'), "span12 isntAOG")
        self.fields['study'].widget.attrs["class"] += " studySearch"

        if parent:
            self.instance.meta_result = parent

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        # todo: removed check, since can't specify instance in formset.
        #  Ideally would be able to check this.
        # if weight is None and self.instance.meta_result.protocol.protocol_type == 0:
        #     raise forms.ValidationError("For meta-analysis epidemiological protocols, the weight-field is required")
        return weight

    def clean(self):
        cleaned_data = super(SingleResultForm, self).clean()

        if int(cleaned_data.get('resultSelector')) == 0:
            if anyNull(cleaned_data, ('n', 'estimate', 'lower_ci', 'upper_ci')):
                raise forms.ValidationError(
                    "If manually entering single-study data, "
                    "N, Risk estimate, and upper and lower CI are required.")
        else:
            if anyNull(cleaned_data, ('study', 'ao', 'outcome_group')):
                raise forms.ValidationError(
                    "If entering single-study data using an Assessed Outcome Group, "
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
        form.fields['study'].queryset = form.fields['study'].queryset\
            .filter(assessment=assessment, study_type=1)
        if form.instance and form.instance.outcome_group:
            form.initial['ao'] = form.instance.outcome_group.assessed_outcome.pk
            form.initial['resultSelector'] = 1


class MetaResultSelectorForm(forms.Form):

    selector = selectable.AutoCompleteSelectField(
        lookup_class=lookups.MetaResultByStudyLookup,
        label='Meta Result',
        widget=selectable.AutoComboboxSelectWidget)

    def __init__(self, *args, **kwargs):
        study_id = kwargs.pop("study_id")
        super(MetaResultSelectorForm, self).__init__(*args, **kwargs)
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span11'
        self.fields['selector'].widget.update_query_parameters(
            {'related': study_id})
