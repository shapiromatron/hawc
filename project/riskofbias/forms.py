from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms.models import BaseModelFormSet, modelformset_factory

from crispy_forms import layout as cfl
from selectable import forms as selectable

from assessment.models import Assessment
from myuser.lookups import AssessmentTeamMemberOrHigherLookup
from study.models import Study
from utils.forms import BaseFormHelper
from . import models


class RobTextForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasAssessment
        fields = ('help_text', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['help_text'].widget.attrs['class'] = 'html5text'
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            'cancel_url': reverse('riskofbias:arob_update',
                                  args=[self.instance.assessment.pk])
        }

        helper = BaseFormHelper(self, **inputs)
        return helper


class RoBDomainForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasDomain
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            'cancel_url': reverse('riskofbias:arob_update',
                                  args=[self.instance.assessment.pk])
        }
        if self.instance.id:
            inputs['legend_text'] = 'Update risk of bias domain'
            inputs['help_text'] = 'Update an existing domain.'
        else:
            inputs['legend_text'] = 'Create new risk of bias domain'
            inputs['help_text'] = 'Create a new risk of bias domain.'

        helper = BaseFormHelper(self, **inputs)
        helper['name'].wrap(cfl.Field, css_class='span6')
        helper['description'].wrap(cfl.Field, css_class='html5text span12')
        return helper

    def clean(self):
        cleaned_data = super().clean()
        if 'name' in self.changed_data and self._meta.model.objects\
                .filter(assessment=self.instance.assessment,
                        name=cleaned_data['name']).count() > 0:
            raise forms.ValidationError('Domain already exists for assessment.')


class RoBMetricForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasMetric
        exclude = ('domain', )

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        if domain:
            self.instance.domain = domain
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            'cancel_url': reverse('riskofbias:arob_update',
                                  args=[self.instance.domain.assessment.pk])
        }
        if self.instance.id:
            inputs['legend_text'] = 'Update risk of bias metric'
            inputs['help_text'] = 'Update an existing metric.'
        else:
            inputs['legend_text'] = 'Create new risk of bias metric'
            inputs['help_text'] = 'Create a new risk of bias metric.'

        helper = BaseFormHelper(self, **inputs)
        helper['name'].wrap(cfl.Field, css_class='span12')
        helper['description'].wrap(cfl.Field, css_class='html5text span12')
        return helper


class RoBScoreForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasScore
        fields = ('metric', 'notes', 'score')

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        self.fields['metric'].widget.attrs['class'] = 'metrics'
        self.fields['score'].widget.attrs['class'] = 'score'
        self.fields['notes'].widget.attrs['class'] = 'html5text'
        self.fields['notes'].widget.attrs['style'] = 'width: 100%;'
        self.fields['notes'].widget.attrs['rows'] = 4
        if study:
            self.instance.study = study


class BaseRoBFormSet(BaseModelFormSet):
    def clean(self):
        """Checks that all metrics are unique."""
        if any(self.errors):
            return
        metrics = []
        for form in self.forms:
            metric = form.cleaned_data['metric']
            if metric in metrics:
                raise forms.ValidationError(
                    'Risk of bias metrics must be unique for each study.')
            metrics.append(metric)


class NumberOfReviewersForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasAssessment
        fields = ('number_of_reviewers',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number_of_reviewers'].initial = \
            self.instance.rob_settings.number_of_reviewers
        self.fields['number_of_reviewers'].help_text = \
            'The number of independent reviewers required for each study. If '\
            'there is more than 1 reviewer, an additional final reviewer will '\
            'resolve any conflicts and make a final determination, so there '\
            'will be a total of N+1 reviews.'
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            'cancel_url': self.instance.rob_settings.get_absolute_url()
        }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper

    def save(self, commit=True):
        instance = super().save(commit)
        if type(instance) is Assessment:
            instance.rob_settings.number_of_reviewers = \
                self.cleaned_data['number_of_reviewers']
            instance.rob_settings.save()
        return instance


class RoBReviewersForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ()

    def __init__(self, *args, **kwargs):
        """
        Adds author fields to form and fills field with assigned reviewer if
        one exists.

         - If the number_of_reviewers on study's assessment is 1, then no
            author fields are generated, only the final_author.
         - If the number_of_reviewers is 2 or more, then int(number_of_reviewers)
            author fields are generated in addition to the final_author field.
        """
        super().__init__(*args, **kwargs)
        self.instance_name = 'Study'
        assessment_id = self.instance.assessment_id
        if hasattr(self.instance_name, 'active_riskofbiases'):
            robs = self.instance.active_riskofbiases
        else:
            robs = self.instance.get_active_robs(with_final=False)

        try:
            reviewers = self.instance.assessment.rob_settings.number_of_reviewers
        except ObjectDoesNotExist:
            reviewers = 0

        if reviewers > 1:
            for i in range(reviewers):
                author_field = 'author-{}'.format(i)
                self.fields[author_field] = selectable.AutoCompleteSelectField(
                    lookup_class=AssessmentTeamMemberOrHigherLookup,
                    label='Reviewer',
                    required=False,
                    widget=selectable.AutoCompleteSelectWidget)
                self.fields[author_field].widget\
                    .update_query_parameters({'related': assessment_id})
                try:
                    self.fields[author_field].initial = robs[i].author.id
                except IndexError:
                    pass

        self.fields['final_author'] = selectable.AutoCompleteSelectField(
            lookup_class=AssessmentTeamMemberOrHigherLookup,
            label='Final Reviewer',
            required=False,
            widget=selectable.AutoCompleteSelectWidget)
        self.fields['final_author'].widget.update_query_parameters(
            {'related': assessment_id})
        try:
            self.fields['final_author'].initial = \
                self.instance.get_final_rob().author.id
        except (AttributeError):
            pass

    def save(self, commit=True):
        """
        We don't delete any riskofbias reviewers, so when changing assigned
        reviewers this will:

         - deactivate the review belonging to the reviewer in the
            initial form.
         - get or create the review for the reviewer submitted in the form.
           - if the review was created, also create and attach
             RiskOfBiasScore instances for each RiskOfBiasMetric.
         - activate the selected review.
        """
        study = super().save(commit)
        changed_reviewer_fields = (
            field
            for field in self.changed_data
            if field != 'reference_ptr')

        for field in changed_reviewer_fields:
            new_author = self.cleaned_data[field]
            options = {
                'study': study,
                'final': bool(field is 'final_author')}

            if self.fields[field].initial:
                deactivate_rob = models.RiskOfBias.objects\
                    .get(author_id=self.fields[field].initial, **options)
                deactivate_rob.deactivate()

            if new_author:
                activate_rob, created = models.RiskOfBias.objects\
                    .get_or_create(author_id=new_author.id, **options)
                if created:
                    activate_rob.build_scores(study.assessment, study)
                activate_rob.activate()


class RiskOfBiasCopyForm(forms.Form):
    assessment = forms.ModelChoiceField(
        label='Existing assessment',
        queryset=Assessment.objects.all(), empty_label=None)

    def setHelper(self):
        inputs = {
            'legend_text': 'Copy risk of bias approach from existing assessments',  # noqa
            'help_text': 'Copy risk of bias metrics and domains from an existing HAWC assessment which you have access to.',  # noqa
            'cancel_url': reverse(
                'riskofbias:arob_detail', args=[self.assessment.id])
        }
        helper = BaseFormHelper(self, **inputs)
        helper.layout.insert(3, cfl.Div(css_id='extra_content_insertion'))
        helper.form_class = None
        return helper

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.assessment = kwargs.pop('assessment', None)
        super().__init__(*args, **kwargs)
        self.fields['assessment'].widget.attrs['class'] = 'span12'
        self.fields['assessment'].queryset = Assessment.objects\
            .get_viewable_assessments(user, exclusion_id=self.assessment.id)
        self.helper = self.setHelper()

    def copy_riskofbias(self):
        models.RiskOfBias\
            .copy_riskofbias(
                self.assessment,
                self.cleaned_data['assessment'])


RoBFormSet = modelformset_factory(
    models.RiskOfBiasScore,
    form=RoBScoreForm,
    formset=BaseRoBFormSet,
    fields=('metric', 'score', 'notes'),
    extra=0)


RoBReviewerFormset = modelformset_factory(
    model=Study,
    form=RoBReviewersForm,
    fields=(),
    extra=0)
