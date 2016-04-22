from django import forms
from django.core.urlresolvers import reverse
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.forms.fields import TextInput

from crispy_forms import layout as cfl
from crispy_forms.helper import FormHelper
from selectable import forms as selectable

from study.models import Study
from . import models

from myuser.lookups import AssessmentTeamMemberOrHigherLookup

class RoBDomainForm(forms.ModelForm):

    class Meta:
        model = models.RiskOfBiasDomain
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(RoBDomainForm, self).__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            "cancel_url": reverse('riskofbias:arob_update', args=[self.instance.assessment.pk])
        }
        if self.instance.id:
            inputs["legend_text"] = u"Update risk-of-bias domain"
            inputs["help_text"]   = u"Update an existing domain."
        else:
            inputs["legend_text"] = u"Create new risk-of-bias domain"
            inputs["help_text"]   = u"Create a new risk-of-bias domain."

        helper = BaseFormHelper(self, **inputs)
        helper['name'].wrap(cfl.Field, css_class="span6")
        helper['description'].wrap(cfl.Field, css_class="html5text span12")
        return helper


class RoBMetricForm(forms.ModelForm):

    class Meta:
        model = models.RiskOfBiasMetric
        exclude = ('domain', )

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('parent', None)
        super(RoBMetricForm, self).__init__(*args, **kwargs)
        if domain:
            self.instance.domain = domain
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            "cancel_url": reverse('riskofbias:arob_update', args=[self.instance.domain.assessment.pk])
        }
        if self.instance.id:
            inputs["legend_text"] = u"Update risk-of-bias metric"
            inputs["help_text"]   = u"Update an existing metric."
        else:
            inputs["legend_text"] = u"Create new risk-of-bias metric"
            inputs["help_text"]   = u"Create a new risk-of-bias metric."

        helper = BaseFormHelper(self, **inputs)
        helper['metric'].wrap(cfl.Field, css_class="span12")
        helper['description'].wrap(cfl.Field, css_class="html5text span12")
        return helper


class RoBScoreForm(forms.ModelForm):

    class Meta:
        model = models.RiskOfBiasScore
        fields = ('metric', 'notes', 'score')

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('parent', None)
        super(RoBScoreForm, self).__init__(*args, **kwargs)
        self.fields['metric'].widget.attrs['class'] = 'metrics'
        self.fields['score'].widget.attrs['class'] = 'score'
        self.fields['notes'].widget.attrs['class'] = 'html5text'
        self.fields['notes'].widget.attrs['style'] = 'width: 100%;'
        self.fields['notes'].widget.attrs['rows'] = 4
        if study:
            self.instance.study = study


class RoBEndpointForm(RoBScoreForm):

    def __init__(self, *args, **kwargs):
        super(RoBEndpointForm, self).__init__(*args, **kwargs)
        self.fields['metric'].queryset = self.fields['metric'].queryset.filter(
            domain__assessment=self.instance.study.assessment)
        self.helper = self.setHelper()

    def setHelper(self):
        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   u"Update a risk-of-bias override.",
            }
        else:
            inputs = {
                "legend_text": u"Create risk-of-bias override",
                "help_text":   u"""
                    Create a risk-of-bias metric which is overridden for this
                    particular endpoint.
                    """,
            }

        inputs["cancel_url"] = self.instance.study.get_absolute_url()

        helper = BaseFormHelper(self, **inputs)
        return helper

    def clean_metric(self):
        metric = self.cleaned_data['metric']
        qualities = self.instance.study.qualities.all()
        for quality in qualities:
            if metric == quality.metric and quality.id != self.instance.id:
                raise forms.ValidationError("Risk-of-bias metrics must be unique for a given endpoint.")
        return metric


class BaseRoBFormSet(BaseModelFormSet):
    def clean(self):
        """Checks that all metrics are unique."""
        if any(self.errors):
            return
        metrics = []
        for form in self.forms:
            metric = form.cleaned_data['metric']
            if metric in metrics:
                raise forms.ValidationError("Risk-of-bias metrics must be unique for a given study.")
            metrics.append(metric)


class NumberOfReviewersForm(forms.ModelForm):
    class Meta:
        model = models.RiskOfBiasReviewers
        fields = ('number',)


class RoBReviewerFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(RoBReviewerFormsetHelper, self).__init__(*args, **kwargs)
        self.template = 'forms/table_inline_formset.html'


class RoBReviewersForm(forms.ModelForm):
    conflict_author = selectable.AutoCompleteSelectField(
        lookup_class=AssessmentTeamMemberOrHigherLookup,
        required=False,
        label="Conflict Resolution author"
    )

    class Meta:
        model = Study
        fields = ('short_citation',)

    def __init__(self, *args, **kwargs):
        super(RoBReviewersForm, self).__init__(*args, **kwargs)
        self.fields['short_citation'].widget.attrs['class'] = 'study'
        self.fields['short_citation'].label = 'Study'
        # reviewers = self.instance.rob_reviewers.first() if self.instance.rob_reviewers.exists() else self.instance.assessment.rob_reviewers.first()
        for i in range(1):
            author_field = "author-{}".format(i)
            self.fields[author_field] = selectable.AutoCompleteSelectField(
                lookup_class=AssessmentTeamMemberOrHigherLookup,
                label='Reviewer',
                widget=selectable.AutoCompleteSelectWidget)
            self.fields[author_field].widget.update_query_parameters(
                {'related': self.instance.assessment_id})
        # set conflict_author as the last field
        self.fields['conflict_author'] = self.fields.pop('conflict_author')


RoBFormSet = modelformset_factory(
    models.RiskOfBiasScore,
    form=RoBScoreForm,
    formset=BaseRoBFormSet,
    fields=('riskofbias', 'metric', 'score', 'notes'),
    extra=0)

RoBReviewerFormset = modelformset_factory(
    model=Study,
    form=RoBReviewersForm,
    fields=('short_citation',),
    extra=0,
)
