from django import forms
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.forms.fields import TextInput

from assessment.models import Assessment
from . import models


class StudyForm(forms.ModelForm):

    class Meta:
        model = models.Study
        fields = ('study_type', 'short_citation', 'full_citation',
                  'coi_reported', 'coi_details', 'funding_source',
                  'study_identifier', 'contact_author', 'ask_author',
                  'summary')

    def __init__(self, *args, **kwargs):
        super(StudyForm, self).__init__(*args, **kwargs)
        for fld in ('full_citation', 'coi_details', 'funding_source', 'ask_author'):
            self.fields[fld].widget.attrs['rows'] = 3

        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'
            else:
                widget.attrs['class'] = 'checkbox'


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = models.Attachment
        fields = ('attachment', )

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('parent', None)
        super(AttachmentForm, self).__init__(*args, **kwargs)
        if study:
            self.instance.study = study


class NewStudyFromReferenceForm(StudyForm):

    def __init__(self, *args, **kwargs):
        reference = kwargs.pop('parent', None)
        super(NewStudyFromReferenceForm, self).__init__(*args, **kwargs)
        if reference:
            self.instance.reference_ptr = reference


class ReferenceStudyForm(StudyForm):

    class Meta:
        model = models.Study
        fields = ('study_type', 'short_citation', 'full_citation',
                  'title', 'authors', 'journal', 'abstract',
                  'coi_reported', 'coi_details', 'funding_source',
                  'study_identifier', 'contact_author', 'ask_author',
                  'summary')

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(ReferenceStudyForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget = TextInput()
        self.fields['authors'].widget = TextInput()
        self.fields['journal'].widget = TextInput()
        if assessment:
            self.instance.assessment = assessment


class StudySearchForm(forms.Form):
    short_citation = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        assessment_pk = kwargs.pop('assessment_pk', None)
        super(StudySearchForm, self).__init__(*args, **kwargs)
        if assessment_pk:
            self.assessment = Assessment.objects.get(pk=assessment_pk)

    def search(self):
        query = {}
        if self.cleaned_data['short_citation']:
            query['short_citation__icontains'] = self.cleaned_data['short_citation']

        response_json = []
        for obj in models.Study.objects.filter(assessment=self.assessment).filter(**query):
            response_json.append(obj.get_json(json_encode=False))
        return response_json


class SQDomainForm(forms.ModelForm):

    class Meta:
        model = models.StudyQualityDomain
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(SQDomainForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'input-xlarge'
        self.fields['description'].widget.attrs['class'] = 'html5text span12'
        if assessment:
            self.instance.assessment = assessment


class SQMetricForm(forms.ModelForm):

    class Meta:
        model = models.StudyQualityMetric
        exclude = ('domain', )

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('parent', None)
        super(SQMetricForm, self).__init__(*args, **kwargs)
        self.fields['metric'].widget.attrs['class'] = 'span12'
        self.fields['description'].widget.attrs['class'] = 'html5text span12'
        if domain:
            self.instance.domain = domain


class SQForm(forms.ModelForm):

    class Meta:
        model = models.StudyQuality
        exclude = ('study', )

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('study', None)
        super(SQForm, self).__init__(*args, **kwargs)
        self.fields['metric'].widget.attrs['class'] = 'metrics'
        self.fields['score'].widget.attrs['class'] = 'score'
        self.fields['notes'].widget.attrs['class'] = 'html5text span12'
        if study:
            self.instance.study = study


class BaseSQFormSet(BaseModelFormSet):
    def clean(self):
        """Checks that all metrics are unique."""
        if any(self.errors):
            return
        metrics = []
        for form in self.forms:
            metric = form.cleaned_data['metric']
            if metric in metrics:
                raise forms.ValidationError("Study quality metrics must be unique for a given study.")
            metrics.append(metric)

SQFormSet = modelformset_factory(models.StudyQuality,
                                 form=SQForm,
                                 formset=BaseSQFormSet,
                                 extra=0)
