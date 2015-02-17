from django import forms
from django.core.urlresolvers import reverse
from django.forms.models import BaseModelFormSet, modelformset_factory
from django.forms.fields import TextInput

from crispy_forms import layout as cfl

from assessment.models import Assessment
from lit.models import Reference
from utils.forms import BaseFormHelper
from . import models


class BaseStudyForm(forms.ModelForm):
    """
    Base form
    """
    class Meta:
        model = models.Study
        fields = ('short_citation', 'study_identifier',
                  'full_citation', 'study_type',
                  'coi_reported', 'coi_details',
                  'funding_source',
                  'contact_author', 'ask_author',
                  'summary', 'published')

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        super(BaseStudyForm, self).__init__(*args, **kwargs)
        if type(parent) is Assessment:
            self.instance.assessment = parent
        elif type(parent) is Reference:
            self.instance.reference_ptr = parent

        self.helper = self.setHelper()

    def setHelper(self, inputs={}):
        for fld in ('full_citation', 'coi_details', 'funding_source', 'ask_author'):
            self.fields[fld].widget.attrs['rows'] = 3
        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'
            else:
                widget.attrs['class'] = 'checkbox'

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        helper.add_fluid_row('short_citation', 2, "span6")
        helper.add_fluid_row('coi_reported', 2, "span6")
        helper.add_fluid_row('contact_author', 2, "span6")
        return helper


class StudyForm(BaseStudyForm):
    """
    Study form used for study-updates
    """
    def setHelper(self):
        inputs = {
            "legend_text": u"Update an existing study",
            "help_text": u"",
            "cancel_url": reverse('study:detail', args=[self.instance.id])
        }
        return super(StudyForm, self).setHelper(inputs)


class NewStudyFromReferenceForm(BaseStudyForm):
    """
    Form to create a new Study from an existing reference.
    """
    def setHelper(self):
        inputs = {
            "legend_text": u"Create a new study from an existing reference",
            "help_text": u"",
            "cancel_url": reverse('lit:ref_list_extract', args=[self.instance.reference_ptr.assessment.id])
        }
        return super(NewStudyFromReferenceForm, self).setHelper(inputs)


class ReferenceStudyForm(BaseStudyForm):
    """
    Form to create both a Reference and Study at the same-time.
    """
    class Meta:
        model = models.Study
        fields = ('short_citation', 'study_identifier',
                  'full_citation',
                  'title', 'authors', 'journal',
                  'abstract', 'study_type',
                  'coi_reported', 'coi_details',
                  'funding_source',
                  'contact_author', 'ask_author',
                  'summary', 'published')

    def setHelper(self):
        self.fields['title'].widget = TextInput()
        self.fields['authors'].widget = TextInput()
        self.fields['journal'].widget = TextInput()
        self.fields['abstract'].widget.attrs['rows'] = 3
        inputs = {
            "legend_text": u"Create a new study",
            "help_text": u"",
            "cancel_url": reverse('study:list', args=[self.instance.assessment.id])
        }
        return super(ReferenceStudyForm, self).setHelper(inputs)


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = models.Attachment
        fields = ('attachment', )

    def __init__(self, *args, **kwargs):
        study = kwargs.pop('parent', None)
        super(AttachmentForm, self).__init__(*args, **kwargs)
        if study:
            self.instance.study = study


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
        if assessment:
            self.instance.assessment = assessment
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            "cancel_url": reverse('study:asq_update', args=[self.instance.assessment.pk])
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


class SQMetricForm(forms.ModelForm):

    class Meta:
        model = models.StudyQualityMetric
        exclude = ('domain', )

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('parent', None)
        super(SQMetricForm, self).__init__(*args, **kwargs)
        if domain:
            self.instance.domain = domain
        self.helper = self.setHelper()

    def setHelper(self):
        inputs = {
            "cancel_url": reverse('study:asq_update', args=[self.instance.domain.assessment.pk])
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


class SQForm(forms.ModelForm):

    class Meta:
        model = models.StudyQuality
        exclude = ('content_type', 'object_id')

    def __init__(self, *args, **kwargs):
        content_object = kwargs.pop('content_object', None)
        super(SQForm, self).__init__(*args, **kwargs)
        self.fields['metric'].widget.attrs['class'] = 'metrics'
        self.fields['score'].widget.attrs['class'] = 'score'
        self.fields['notes'].widget.attrs['class'] = 'html5text span12'
        self.fields['notes'].widget.attrs['rows'] = 4
        if content_object:
            self.instance.content_object = content_object


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
