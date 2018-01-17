from django import forms
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.utils.functional import curry

from crispy_forms import bootstrap as cfb
from crispy_forms import layout as cfl
from selectable import forms as selectable

from assessment.lookups import BaseEndpointLookup, EffectTagLookup
from assessment.models import DoseUnits
from study.lookups import EpiStudyLookup
from utils.forms import BaseFormHelper, CopyAsNewSelectorForm
from utils.helper import tryParseInt

from . import models, lookups


class CriteriaForm(forms.ModelForm):

    CREATE_LEGEND = "Create new study criteria"

    CREATE_HELP_TEXT = """
        Create a epidemiology study criteria. Study criteria can be applied to
        study populations as inclusion criteria, exclusion criteria, or
        confounding criteria. They are assessment-specific. Please take care
        not to duplicate existing factors."""

    class Meta:
        model = models.Criteria
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.CriteriaLookup,
            allow_new=True)
        self.instance.assessment = assessment
        for fld in list(self.fields.keys()):
            self.fields[fld].widget.attrs['class'] = 'span12'
        self.fields['description'].widget.update_query_parameters(
            {'related': self.instance.assessment.id})
        self.helper = self.setHelper()

    def clean(self):
        super().clean()
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
        for fld in list(self.fields.keys()):
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

    CREATE_LEGEND = "Create new study-population"

    CREATE_HELP_TEXT = """
        Create a new study population. Each study-population is a
        associated with an epidemiology study. There may be
        multiple study populations with a single study,
        though this is typically unlikely."""

    UPDATE_HELP_TEXT = "Update an existing study-population."

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
        super().__init__(*args, **kwargs)
        self.fields['comments'] = self.fields.pop('comments')  # move to end
        self.fields['region'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.RegionLookup,
            allow_new=True)
        self.fields['state'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.StateLookup,
            allow_new=True)
        if study:
            self.instance.study = study

        for fld in self.CRITERION_FIELDS:
            self.fields[fld].widget.update_query_parameters(
                {'related': self.instance.study.assessment_id})
            if self.instance.id:
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
        instance = super().save(commit)
        if commit:
            self.save_criteria()
        return instance

    def setHelper(self):
        for fld in list(self.fields.keys()):
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
                "legend_text": "Update {}".format(self.instance),
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
        helper.add_fluid_row('age_profile', 2, "span6")
        helper.add_fluid_row('country', 3, "span4")
        helper.add_fluid_row('eligible_n', 3, "span4")
        helper.add_fluid_row('inclusion_criteria', 3, "span4")

        url = reverse('epi:studycriteria_create',
                      kwargs={'pk': self.instance.study.assessment.pk})
        helper.addBtnLayout(helper.layout[6], 0, url, "Create criteria", "span4")
        helper.addBtnLayout(helper.layout[6], 1, url, "Create criteria", "span4")
        helper.addBtnLayout(helper.layout[6], 2, url, "Create criteria", "span4")

        return helper


class StudyPopulationSelectorForm(CopyAsNewSelectorForm):
    label = 'Study Population'
    lookup_class = lookups.StudyPopulationByStudyLookup


class AdjustmentFactorForm(forms.ModelForm):

    CREATE_LEGEND = "Create new adjustment factor"

    CREATE_HELP_TEXT = """
        Create a new adjustment factor. Adjustment factors can be applied to
        outcomes as applied or considered factors.
        They are assessment-specific.
        Please take care not to duplicate existing factors."""

    class Meta:
        model = models.AdjustmentFactor
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        self.fields['description'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.AdjustmentFactorLookup,
            allow_new=True)
        self.instance.assessment = assessment
        for fld in list(self.fields.keys()):
            self.fields[fld].widget.attrs['class'] = 'span12'
        self.fields['description'].widget.update_query_parameters(
            {'related': self.instance.assessment.id})
        self.helper = self.setHelper()

    def clean(self):
        super().clean()
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
        for fld in list(self.fields.keys()):
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
        model = models.Exposure
        exclude = ('study_population', )

    def __init__(self, *args, **kwargs):
        study_population = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        self.fields['measured'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.ExposureMeasuredLookup,
            allow_new=True)
        self.fields['metric'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.ExposureMetricLookup,
            allow_new=True)
        self.fields['age_of_exposure'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.AgeOfExposureLookup,
            allow_new=True)
        if study_population:
            self.instance.study_population = study_population
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in list(self.fields.keys()):
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
                "legend_text": "Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": "Create new exposure",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study_population.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('inhalation', 6, "span2")
        helper.add_fluid_row('measured', 3, "span4")
        helper.add_fluid_row('metric_description', 3, "span4")
        helper.add_fluid_row('age_of_exposure', 3, "span6")
        helper.add_fluid_row('n', 3, "span4")
        helper.add_fluid_row('variance', 2, "span6")
        helper.add_fluid_row('lower_ci', 4, "span3")

        url = reverse(
            'assessment:dose_units_create',
            kwargs={'pk': self.instance.study_population.study.assessment_id}
        )
        helper.addBtnLayout(helper.layout[4], 2, url, "Create units", "span4")

        return helper


class ExposureSelectorForm(CopyAsNewSelectorForm):
    label = 'Exposure'
    lookup_class = lookups.ExposureByStudyPopulationLookup


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
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = selectable.AutoCompleteWidget(
            lookup_class=BaseEndpointLookup,
            allow_new=True)
        self.fields['system'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.SystemLookup,
            allow_new=True)
        self.fields['effect'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EffectLookup,
            allow_new=True)
        self.fields['effect_subtype'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.EffectSubtypeLookup,
            allow_new=True)
        self.fields['age_of_measurement'].widget = selectable.AutoCompleteWidget(
            lookup_class=lookups.AgeOfMeasurementLookup,
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
        for fld in list(self.fields.keys()):
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
                "legend_text": "Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": "Create new outcome",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.study_population.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 2, "span6")
        helper.add_fluid_row('system', 3, "span4")
        helper.add_fluid_row('diagnostic', 2, "span6")
        helper.add_fluid_row('outcome_n', 2, "span6")

        url = reverse(
            'assessment:effect_tag_create',
            kwargs={'pk': self.instance.assessment.pk}
        )
        helper.addBtnLayout(helper.layout[2], 1, url, "Add new effect tag", "span6")

        return helper


class OutcomeFilterForm(forms.Form):

    ORDER_BY_CHOICES = (
        ('study_population__study__short_citation', 'study'),
        ('study_population__name', 'study population'),
        ('name', 'outcome name'),
        ('system', 'system'),
        ('effect', 'effect'),
        ('diagnostic', 'diagnostic'),
    )

    studies = selectable.AutoCompleteSelectMultipleField(
        label='Study reference',
        lookup_class=EpiStudyLookup,
        help_text="ex: Smith et al. 2010",
        required=False)

    name = forms.CharField(
        label='Outcome name',
        widget=selectable.AutoCompleteWidget(lookups.OutcomeLookup),
        help_text="ex: blood, glucose",
        required=False)

    study_population = forms.CharField(
        label='Study population',
        widget=selectable.AutoCompleteWidget(lookups.StudyPopulationByAssessmentLookup),
        help_text="ex: population near a Teflon manufacturing plant",
        required=False)

    metric = forms.CharField(
        label='Measurement metric',
        widget=selectable.AutoCompleteWidget(lookups.RelatedExposureMetricLookup),
        help_text="ex: drinking water",
        required=False)

    age_profile = forms.CharField(
        label='Age profile',
        widget=selectable.AutoCompleteWidget(lookups.RelatedStudyPopulationAgeProfileLookup),
        help_text="ex: children",
        required=False)

    source = forms.CharField(
        label='Study population source',
        widget=selectable.AutoCompleteWidget(lookups.RelatedStudyPopulationSourceLookup),
        help_text="ex: occupational exposure",
        required=False)

    country = forms.CharField(
        label='Study population country',
        widget=selectable.AutoCompleteWidget(lookups.RelatedCountryNameLookup),
        help_text="ex: Japan",
        required=False)

    design = forms.MultipleChoiceField(
        label='Study design',
        choices=models.StudyPopulation.DESIGN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=[c[0] for c in models.StudyPopulation.DESIGN_CHOICES],
        required=False)

    system = forms.CharField(
        label='System',
        widget=selectable.AutoCompleteWidget(lookups.RelatedSystemLookup),
        help_text="ex: immune and lymphatic system",
        required=False)

    effect = forms.CharField(
        label='Effect',
        widget=selectable.AutoCompleteWidget(lookups.RelatedEffectLookup),
        help_text="ex: Cancer",
        required=False)

    effect_subtype = forms.CharField(
        label='Effect subtype',
        widget=selectable.AutoCompleteWidget(lookups.RelatedEffectSubtypeLookup),
        help_text="ex: Melanoma",
        required=False)

    diagnostic = forms.MultipleChoiceField(
        choices=models.Outcome.DIAGNOSTIC_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=[c[0] for c in models.Outcome.DIAGNOSTIC_CHOICES],
        required=False)

    order_by = forms.ChoiceField(
        choices=ORDER_BY_CHOICES,
    )

    paginate_by = forms.IntegerField(
        label='Items per page',
        min_value=1,
        initial=25,
        max_value=10000,
        required=False)

    def __init__(self, *args, **kwargs):
        assessment_id = kwargs.pop('assessment_id')
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ('design', 'diagnostic', 'order_by', 'paginate_by'):
                self.fields[field].widget.update_query_parameters(
                    {'related': assessment_id})

        self.helper = self.setHelper()

    def setHelper(self):

        # by default take-up the whole row-fluid
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) not in [forms.CheckboxInput, forms.CheckboxSelectMultiple]:
                widget.attrs['class'] = 'span12'

        helper = BaseFormHelper(self)

        helper.form_method = "GET"
        helper.form_class = None

        helper.add_fluid_row('studies', 4, "span3")
        helper.add_fluid_row('age_profile', 4, "span3")
        helper.add_fluid_row('system', 4, "span3")

        helper.layout.append(
            cfb.FormActions(
                cfl.Submit('submit', 'Apply filters'),
            )
        )

        return helper

    def get_query(self):

        studies = self.cleaned_data.get('studies')
        name = self.cleaned_data.get('name')
        study_population = self.cleaned_data.get('study_population')
        metric = self.cleaned_data.get('metric')
        age_profile = self.cleaned_data.get('age_profile')
        source = self.cleaned_data.get('source')
        country = self.cleaned_data.get('country')
        design = self.cleaned_data.get('design')
        system = self.cleaned_data.get('system')
        effect = self.cleaned_data.get('effect')
        effect_subtype = self.cleaned_data.get('effect_subtype')
        diagnostic = self.cleaned_data.get('diagnostic')

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
            query &= Q(study_population__country__name__icontains=country)
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
        return query

    def get_order_by(self):
        return self.cleaned_data.get('order_by', self.ORDER_BY_CHOICES[0][0])


class OutcomeSelectorForm(CopyAsNewSelectorForm):
    label = 'Outcome'
    lookup_class = lookups.OutcomeByStudyPopulationLookup


class ComparisonSet(forms.ModelForm):

    HELP_TEXT_CREATE = """Create a new comparison set. Each group is a
        collection of people, and all groups in this collection are
        comparable to one-another. For example, you may a new comparison set
        which contains two groups: cases and controls. Alternatively, for
        cohort-based studies, you may create a new comparison set with four
        different groups, one for each quartile of exposure based on exposure
        measurements.
    """
    HELP_TEXT_UPDATE = """Update an existing comparison set."""

    class Meta:
        model = models.ComparisonSet
        exclude = ('study_population', 'outcome')

    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent', None)
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

        self.helper = self.setHelper()

    def setHelper(self):
        for fld in list(self.fields.keys()):
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
                "legend_text": "Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": url
            }
        else:
            inputs = {
                "legend_text": "Create new comparison set",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.parent.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper


class ComparisonSetByStudyPopulationSelectorForm(CopyAsNewSelectorForm):
    label = 'Comparison set'
    lookup_class = lookups.ComparisonSetByStudyPopulationLookup


class ComparisonSetByOutcomeSelectorForm(CopyAsNewSelectorForm):
    label = 'Comparison set'
    lookup_class = lookups.ComparisonSetByOutcomeLookup


class GroupForm(forms.ModelForm):

    class Meta:
        model = models.Group
        exclude = ('comparison_set', 'group_id')


class SingleGroupForm(GroupForm):

    HELP_TEXT_UPDATE = """Update an existing group and group descriptions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in list(self.fields.keys()):
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'
            if type(widget) == forms.Textarea:
                widget.attrs['rows'] = 3

        inputs = {
            "legend_text": "Update {}".format(self.instance),
            "help_text": self.HELP_TEXT_UPDATE,
            "cancel_url": self.instance.get_absolute_url()
        }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('name', 3, "span4")
        helper.add_fluid_row('sex', 2, "span6")
        helper.add_fluid_row('eligible_n', 3, "span4")
        return helper


class BaseGroupFormset(BaseModelFormSet):

    def clean(self):
        super().clean()

        # check that there is at least one exposure-group
        count = len([f for f in self.forms if f.is_valid() and f.clean()])
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

    HELP_TEXT_CREATE = """Describe results found for measured outcome."""
    HELP_TEXT_UPDATE = """Update results found for measured outcome."""
    ADJUSTMENT_FIELDS = ["factors_applied", "factors_considered"]

    factors_applied = selectable.AutoCompleteSelectMultipleField(
        help_text="All factors included in final model"
        ,lookup_class=lookups.AdjustmentFactorLookup
        ,required=False
    )

    factors_considered = selectable.AutoCompleteSelectMultipleField(
        label="Adjustment factors considered"
        ,help_text="Factors considered, but not included in the final model"
        ,lookup_class=lookups.AdjustmentFactorLookup
        ,required=False
    )

    class Meta:
        model = models.Result
        exclude = ('outcome', 'adjustment_factors')

    def __init__(self, *args, **kwargs):
        outcome = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

        self.fields['comments'] = self.fields.pop('comments')  # move to end

        if outcome:
            self.instance.outcome = outcome
        else:
            outcome = self.instance.outcome

        self.fields["comparison_set"].queryset = models.ComparisonSet.objects\
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
        instance = super().save(commit)
        if commit:
            self.save_factors()
        return instance

    def setHelper(self):
        for fld in list(self.fields.keys()):
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
                "legend_text": "Update {}".format(self.instance),
                "help_text": self.HELP_TEXT_UPDATE,
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": "Create new set of results",
                "help_text": self.HELP_TEXT_CREATE,
                "cancel_url": self.instance.outcome.get_absolute_url()
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None

        helper.add_fluid_row('name', 2, "span6")
        helper.add_fluid_row('metric', 2, "span6")
        helper.add_fluid_row('data_location', 2, "span6")
        helper.add_fluid_row('dose_response', 3, "span4")
        helper.add_fluid_row('statistical_power', 4, "span3")
        helper.add_fluid_row('factors_applied', 2, "span6")
        helper.add_fluid_row('estimate_type', 3, "span4")
        helper.add_fluid_row("resulttags", 1, "span6")

        url = reverse('assessment:effect_tag_create', kwargs={'pk': self.instance.outcome.assessment_id})
        helper.addBtnLayout(helper.layout[8], 0, url, "Add new result tag", "span6")

        url = reverse('epi:adjustmentfactor_create', kwargs={'pk': self.instance.outcome.assessment_id})
        helper.addBtnLayout(helper.layout[9], 0, url, "Add new adjustment factor", "span6")
        helper.addBtnLayout(helper.layout[9], 1, url, "Add new adjustment factor", "span6")

        return helper


class ResultSelectorForm(CopyAsNewSelectorForm):
    label = 'Result'
    lookup_class = lookups.ResultByOutcomeLookup


class ResultUpdateForm(ResultForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comparison_set'].widget.attrs['disabled'] = True


class GroupResultForm(forms.ModelForm):

    class Meta:
        model = models.GroupResult
        exclude = ('result', )

    def __init__(self, *args, **kwargs):
        study_population = kwargs.pop('study_population', None)
        outcome = kwargs.pop('outcome', None)
        result = kwargs.pop('result', None)
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = models.Group.objects\
            .filter(
                Q(comparison_set__study_population=study_population) |
                Q(comparison_set__outcome=outcome)
            )
        if result:
            self.instance.result = result
        self.helper = self.setHelper()

    def setHelper(self):
        for fld in list(self.fields.keys()):
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
        super().__init__(**kwargs)
        self.form = curry(
            self.form,
            study_population=study_population,
            outcome=outcome,
            result=self.result
        )

    def clean(self):
        super().clean()

        # check that there is at least one result-group
        count = len([f for f in self.forms if f.is_valid() and f.clean()])
        if count < 1:
            raise forms.ValidationError("At least one group is required.")

        mfs = 0
        for form in self.forms:
            if form.cleaned_data['is_main_finding']:
                mfs += 1

        if mfs > 1:
            raise forms.ValidationError("Only one-group can be the main-finding.")

        if self.result:
            comparison_set_id = self.result.comparison_set_id
        else:
            comparison_set_id = tryParseInt(self.data['comparison_set'], -1)

        # exit early if any individual form is invalid
        if any([not form.is_valid() for form in self.forms]):
            return

        # Ensure all groups in group collection are accounted for,
        # and no other groups exist
        group_ids = [form.cleaned_data['group'].id for form in self.forms]
        selectedGroups = models.Group.objects\
            .filter(id__in=group_ids, comparison_set_id=comparison_set_id)
        allGroups = models.Group.objects\
            .filter(comparison_set_id=comparison_set_id)
        if selectedGroups.count() != allGroups.count():
            raise forms.ValidationError("Missing group(s) in this comparison set")


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
