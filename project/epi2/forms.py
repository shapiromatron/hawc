from django import forms
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.functional import curry

from crispy_forms import layout as cfl
from selectable import forms as selectable

from assessment.lookups import BaseEndpointLookup, EffectTagLookup
from utils.forms import BaseFormHelper

from . import models, lookups


class CriteriaForm(forms.ModelForm):

    CREATE_LEGEND = u"Create new study criteria"

    CREATE_HELP_TEXT = u"""
        Create a epidemiology study criteria. Study criteria can be applied to
        study populations as inclusion criteria, exclusion criteria, or
        confounding criteria. They are assessment-specific. Please take care
        not to duplicate existing factors."""

    class Meta:
        model = models.Criteria
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(CriteriaForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.CriteriaLookup,
            allow_new=True)
        self.instance.assessment = assessment
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span12'
        self.fields['description'].widget.update_query_parameters(
            {'related': self.instance.assessment.id})
        self.helper = self.setHelper()

    def clean(self):
        super(CriteriaForm, self).clean()
        # assessment-description unique-together constraint check must be
        # added since assessment is not included on form
        pk = getattr(self.instance, 'pk', None)
        crits = models.Criteria.objects \
            .filter(assessment=self.instance.assessment,
                    description=self.cleaned_data.get('description', "")) \
            .exclude(pk=pk)

        if crits.count() > 0:
            self.add_error("description", "Must be unique for assessment")

        return self.cleaned_data

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

        inputs = {
            "legend_text": self.CREATE_LEGEND,
            "help_text":   self.CREATE_HELP_TEXT,
            "form_actions": [
                cfl.Submit('save', 'Save'),
                cfl.HTML("""<a class="btn" href='#' onclick='window.close()'>Cancel</a>"""),
            ]
        }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper


class StudyPopulationForm(forms.ModelForm):

    CREATE_LEGEND = u"Create new study-population"

    CREATE_HELP_TEXT = u"""
        Create a new study population. Each study-population is a
        associated with an epidemiology study. There may be
        multiple study populations with a single study,
        though this is typically unlikely."""

    UPDATE_HELP_TEXT = u"Update an existing study-population."

    CRITERION_FIELDS = [
        "inclusion_criteria",
        "exclusion_criteria",
        "confounding_criteria"
    ]

    CRITERION_TYPE_CW = {
        "inclusion_criteria": "I",
        "exclusion_criteria": "E",
        "confounding_criteria": "C",
    }

    inclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.CriteriaLookup,
        required=False)

    exclusion_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.CriteriaLookup,
        required=False)

    confounding_criteria = selectable.AutoCompleteSelectMultipleField(
        lookup_class=lookups.CriteriaLookup,
        required=False)

    class Meta:
        model = models.StudyPopulation
        exclude = ('study', 'criteria')

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('parent', None)
        super(StudyPopulationForm, self).__init__(*args, **kwargs)
        self.fields['comments'] = self.fields.pop('comments')  # move to end
        self.fields['region'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.RegionLookup,
            allow_new=True)
        self.fields['state'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.StateLookup,
            allow_new=True)
        if study:
            self.instance.study = study
        if self.instance.id:
            for fld in self.CRITERION_FIELDS:
                self.fields[fld].initial = getattr(self.instance, fld)
        self.helper = self.setHelper()

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
                objs.append(models.StudyPopulationCriteria(
                    criteria=criteria,
                    study_population=self.instance,
                    criteria_type=self.CRITERION_TYPE_CW[field]))
        models.StudyPopulationCriteria.objects.bulk_create(objs)

    def save(self, commit=True):
        instance = super(StudyPopulationForm, self).save(commit)
        if commit:
            self.save_criteria()
        return instance

    def setHelper(self):
        for fld in self.CRITERION_FIELDS:
            self.fields[fld].widget.update_query_parameters(
                {'related': self.instance.study.assessment_id})
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld in self.CRITERION_FIELDS:
                    widget.attrs['class'] = 'span10'
                else:
                    widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   self.UPDATE_HELP_TEXT,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": self.CREATE_LEGEND,
                "help_text":   self.CREATE_HELP_TEXT,
                "cancel_url": self.instance.study.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 2, "span6")
        helper.add_fluid_row('country', 3, "span4")
        helper.add_fluid_row('eligible_n', 3, "span4")
        helper.add_fluid_row('inclusion_criteria', 3, "span4")

        url = reverse('epi2:studycriteria_create',
                      kwargs={'pk': self.instance.study.assessment.pk})
        helper.addBtnLayout(helper.layout[5], 0, url, "Create criteria", "span4")
        helper.addBtnLayout(helper.layout[5], 1, url, "Create criteria", "span4")
        helper.addBtnLayout(helper.layout[5], 2, url, "Create criteria", "span4")

        return helper


class AdjustmentFactorForm(forms.ModelForm):

    CREATE_LEGEND = u"Create new adjustment factor"

    CREATE_HELP_TEXT = u"""
        Create a new adjustment factor. Adjustment factors can be applied to
        outcomes as applied or considered factors.
        They are assessment-specific.
        Please take care not to duplicate existing factors."""

    class Meta:
        model = models.AdjustmentFactor
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(AdjustmentFactorForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.AdjustmentFactorLookup,
            allow_new=True)
        self.instance.assessment = assessment
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span12'
        self.fields['description'].widget.update_query_parameters(
            {'related': self.instance.assessment.id})
        self.helper = self.setHelper()

    def clean(self):
        super(AdjustmentFactorForm, self).clean()
        # assessment-description unique-together constraint check must be
        # added since assessment is not included on form
        pk = getattr(self.instance, 'pk', None)
        crits = models.AdjustmentFactor.objects \
            .filter(assessment=self.instance.assessment,
                    description=self.cleaned_data.get('description', "")) \
            .exclude(pk=pk)

        if crits.count() > 0:
            self.add_error("description", "Must be unique for assessment")

        return self.cleaned_data

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

        inputs = {
            "legend_text": self.CREATE_LEGEND,
            "help_text":   self.CREATE_HELP_TEXT,
            "form_actions": [
                cfl.Submit('save', 'Save'),
                cfl.HTML("""<a class="btn" href='#' onclick='window.close()'>Cancel</a>"""),
            ]
        }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper


class ExposureForm(forms.ModelForm):

    HELP_TEXT_CREATE = """Create a new exposure."""
    HELP_TEXT_UPDATE = """Update an existing exposure."""

    class Meta:
        model = models.Exposure2
        exclude = ('study_population', )

    def __init__(self, *args, **kwargs):
        study_population = kwargs.pop('parent', None)
        super(ExposureForm, self).__init__(*args, **kwargs)
        if study_population:
            self.instance.study_population = study_population
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld in ["metric_units"]:
                    widget.attrs['class'] = 'span10'
                else:
                    widget.attrs['class'] = 'span12'

            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new exposure",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study_population.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('inhalation', 6, "span2")
        helper.add_fluid_row('metric', 3, "span4")
        helper.add_fluid_row('analytical_method', 2, "span6")
        helper.add_fluid_row('duration', 2, "span6")

        url = reverse(
            'assessment:dose_units_create',
            kwargs={'pk': self.instance.study_population.study.assessment_id}
        )
        helper.addBtnLayout(helper.layout[4], 1, url, "Create units", "span4")

        return helper


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
        exclude = ('assessment', 'study_population')

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('assessment', None)
        study_population = kwargs.pop('parent', None)
        super(OutcomeForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = selectable.AutoCompleteWidget(
            lookup_class=BaseEndpointLookup,
            allow_new=True)
        self.fields['effect'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EffectLookup,
            allow_new=True)
        self.fields['effects'].widget = selectable.AutoCompleteSelectMultipleWidget(
            lookup_class=EffectTagLookup)
        self.fields['effects'].help_text = 'Tags used to help categorize effect description.'
        if assessment:
            self.instance.assessment = assessment
        if study_population:
            self.instance.study_population = study_population

        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld in ["effects"]:
                    widget.attrs['class'] = 'span10'
                else:
                    widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new outcome",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study_population.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 3, "span4")
        helper.add_fluid_row('diagnostic', 2, "span6")

        url = reverse(
            'assessment:effect_tag_create',
            kwargs={'pk': self.instance.assessment.pk}
        )
        helper.addBtnLayout(helper.layout[2], 1, url, "Add new effect tag", "span4")

        return helper


class GroupCollection(forms.ModelForm):

    HELP_TEXT_CREATE = """Create a collection of groups. Each group is a
        collection of people, and all groups in this collection may be
        comparable to one-another. For example, you may a set group which
        contains cases and controls (with a group-collection name of
        case-control), or you may have a group of individuals with which
        blood serum levels were collected, and each group is a different
        quartile of exposure.
    """
    HELP_TEXT_UPDATE = """Update an existing group and group collection."""

    class Meta:
        model = models.GroupCollection
        exclude = ('study_population', 'outcome')

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
        super(GroupCollection, self).__init__(*args, **kwargs)
        if self.parent:
            if type(self.parent).__name__ == "StudyPopulation":
                self.instance.study_population = self.parent
            elif type(self.parent).__name__ == "Outcome":
                self.instance.outcome = self.parent

        filters = {}
        if self.instance.study_population:
            filters["study_population"] = self.instance.study_population
        else:
            filters["study_population"] = self.instance.outcome.study_population
        self.fields["exposure"].queryset = self.fields["exposure"].queryset.filter(**filters)

        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            if self.instance.outcome:
                url = self.instance.outcome.get_absolute_url()
            else:
                url = self.instance.study_population.get_absolute_url()
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": url
            }
        else:
            inputs = {
                "legend_text": u"Create new collection of groups",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.parent.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper


class GroupForm(forms.ModelForm):

    class Meta:
        model = models.Group
        exclude = ('collection', 'group_id')


class SingleGroupForm(GroupForm):

    HELP_TEXT_UPDATE = """Update an existing group and group descriptions."""

    def __init__(self, *args, **kwargs):
        super(SingleGroupForm, self).__init__(*args, **kwargs)
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        inputs = {
            "legend_text": u"Update {}".format(self.instance),
            "help_text": self.HELP_TEXT_UPDATE,
            "cancel_url": self.instance.get_absolute_url()
        }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 3, "span4")
        helper.add_fluid_row('sex', 2, "span6")
        helper.add_fluid_row('eligible_n', 3, "span4")
        helper.add_fluid_row('fraction_male', 3, "span4")
        return helper


class BaseGroupFormset(BaseModelFormSet):

    def clean(self):
        super(BaseGroupFormset, self).clean()

        # check that there is at least one exposure-group
        count = len(filter(lambda f: f.is_valid() and f.clean(), self.forms))
        if count < 1:
            raise forms.ValidationError("At least one group is required.")


GroupFormset = modelformset_factory(
    models.Group,
    form=GroupForm,
    formset=BaseGroupFormset,
    can_delete=True,
    extra=0)


BlankGroupFormset = modelformset_factory(
    models.Group,
    form=GroupForm,
    formset=BaseGroupFormset,
    can_delete=False,
    extra=1)


class GroupNumericalDescriptionsForm(forms.ModelForm):

    class Meta:
        model = models.GroupNumericalDescriptions
        exclude = ('group', )


class BaseGroupNumericalDescriptionsFormset(BaseModelFormSet):
    pass


GroupNumericalDescriptionsFormset = modelformset_factory(
    models.GroupNumericalDescriptions,
    form=GroupNumericalDescriptionsForm,
    formset=BaseGroupNumericalDescriptionsFormset,
    can_delete=True,
    extra=1)


class ResultForm(forms.ModelForm):

    HELP_TEXT_CREATE = """Add."""
    HELP_TEXT_UPDATE = """Add."""
    ADJUSTMENT_FIELDS = ["factors_applied", "factors_considered"]

    factors_applied = selectable.AutoCompleteSelectMultipleField(
        help_text="All factors included in final model",
        lookup_class=lookups.AdjustmentFactorLookup,
        required=False)

    factors_considered = selectable.AutoCompleteSelectMultipleField(
        label="Adjustment factors considered",
        help_text="Factors considered, but not included in the final model",
        lookup_class=lookups.AdjustmentFactorLookup,
        required=False)

    class Meta:
        model = models.Result
        exclude = ('outcome', 'adjustment_factors')

    def __init__(self, *args, **kwargs):
        outcome = kwargs.pop('parent', None)
        super(ResultForm, self).__init__(*args, **kwargs)
        self.fields['comments'] = self.fields.pop('comments')  # move to end

        if outcome:
            self.instance.outcome = outcome
        else:
            outcome = self.instance.outcome

        self.fields["groups"].queryset = models.GroupCollection.objects\
            .filter(
                Q(study_population=outcome.study_population) |
                Q(outcome=outcome)
            )

        for fld in self.ADJUSTMENT_FIELDS:
            self.fields[fld].widget.update_query_parameters(
                {'related': self.instance.outcome.assessment_id})
            if self.instance.id:
                self.fields[fld].initial = getattr(self.instance, fld)

        self.helper = self.setHelper()

    def save_factors(self):
        """
        Adjustment factors is a through model; requires the inclusion type.
        We save the m2m relations using the additional information from the
        field-name
        """
        self.instance.resfactors.all().delete()
        objs = []

        applied = self.cleaned_data.get("factors_applied", [])
        objs.extend([
            models.ResultAdjustmentFactor(
                    adjustment_factor=af,
                    result=self.instance,
                    included_in_final_model=True)
            for af in applied
        ])

        considered = self.cleaned_data.get("factors_considered", [])
        considered = set(considered) - set(applied)
        objs.extend([
            models.ResultAdjustmentFactor(
                    adjustment_factor=af,
                    result=self.instance,
                    included_in_final_model=False)
            for af in considered
        ])

        models.ResultAdjustmentFactor.objects.bulk_create(objs)

    def save(self, commit=True):
        instance = super(ResultForm, self).save(commit)
        if commit:
            self.save_factors()
        return instance

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                if fld in self.ADJUSTMENT_FIELDS:
                    widget.attrs['class'] = 'span10'
                else:
                    widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new set of results",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.outcome.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None

        helper.add_fluid_row('metric', 2, "span6")
        helper.add_fluid_row('data_location', 2, "span6")
        helper.add_fluid_row('dose_response', 2, "span6")
        helper.add_fluid_row('statistical_power', 2, "span6")
        helper.add_fluid_row('factors_applied', 2, "span6")
        helper.add_fluid_row('estimate_type', 3, "span4")

        url = reverse('epi2:adjustmentfactor_create',
                      kwargs={'pk': self.instance.outcome.assessment_id})
        helper.addBtnLayout(helper.layout[9], 0, url, "Add new adjustment factor", "span6")
        helper.addBtnLayout(helper.layout[9], 1, url, "Add new adjustment factor", "span6")

        return helper


class ResultUpdateForm(ResultForm):

    def __init__(self, *args, **kwargs):
        super(ResultUpdateForm, self).__init__(*args, **kwargs)
        self.fields['groups'].widget.attrs['disabled'] = True


class GroupResultForm(forms.ModelForm):

    class Meta:
        model = models.GroupResult
        exclude = ('measurement', )

    def __init__(self, *args, **kwargs):
        study_population = kwargs.pop('study_population', None)
        outcome = kwargs.pop('outcome', None)
        result = kwargs.pop('result', None)
        super(GroupResultForm, self).__init__(*args, **kwargs)
        self.fields["group"].queryset = models.Group.objects\
            .filter(
                Q(collection__study_population=study_population) |
                Q(collection__outcome=outcome)
            )
        if result:
            self.instance.measurement = result
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if fld == "group":
                widget.attrs['class'] = "groupField"
                widget.attrs['style'] = "display: none;"
            if fld == "n":
                widget.attrs['class'] = "nField"

        helper = BaseFormHelper(self)
        helper.form_tag = False

        return helper


class BaseGroupResultFormset(BaseModelFormSet):

    def __init__(self, **kwargs):
        study_population = kwargs.pop('study_population', None)
        outcome = kwargs.pop('outcome', None)
        self.result = kwargs.pop('result', None)
        super(BaseGroupResultFormset, self).__init__(**kwargs)
        self.form = curry(self.form, study_population=study_population, outcome=outcome, result=self.result)

    def clean(self):
        super(BaseGroupResultFormset, self).clean()

        # check that there is at least one result-group
        count = len(filter(lambda f: f.is_valid() and f.clean(), self.forms))
        if count < 1:
            raise forms.ValidationError("At least one group is required.")

        # Ensure all groups in group collection are accounted for, and no other
        # groups exist
        group_ids = [form.cleaned_data['group'].id for form in self.forms]
        if self.result:
            collection_id = self.result.groups_id
        else:
            collection_id = int(self.data['groups'])
        selectedGroups = models.Group.objects\
            .filter(id__in=group_ids, collection_id=collection_id)
        allGroups = models.Group.objects\
            .filter(collection_id=collection_id)
        if selectedGroups.count() != allGroups.count():
            raise forms.ValidationError("Missing a result-group for this result-collection")


GroupResultFormset = modelformset_factory(
    models.GroupResult,
    form=GroupResultForm,
    formset=BaseGroupResultFormset,
    can_delete=False,
    extra=0)


BlankGroupResultFormset = modelformset_factory(
    models.GroupResult,
    form=GroupResultForm,
    formset=BaseGroupResultFormset,
    can_delete=False,
    extra=1)
