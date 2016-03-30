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
                  'funding_source', 'full_text_url',
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
        if 'authors' in self.fields:
            helper.add_fluid_row('authors', 2, "span6")
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
                  'funding_source', 'full_text_url',
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
        fields = ('metric', 'notes', 'score')

    def __init__(self, *args, **kwargs):
        content_object = kwargs.pop('parent', None)
        super(SQForm, self).__init__(*args, **kwargs)
        self.fields['metric'].widget.attrs['class'] = 'metrics'
        self.fields['score'].widget.attrs['class'] = 'score'
        self.fields['notes'].widget.attrs['class'] = 'html5text'
        self.fields['notes'].widget.attrs['style'] = 'width: 100%;'
        self.fields['notes'].widget.attrs['rows'] = 4
        if content_object:
            self.instance.content_object = content_object

class SQAuthorForm(forms.Form):
    author = forms.BooleanField(
        label='Authorship',
        help_text='This Risk of Bias assessment has no author. Select to take authorship.',
        required=False
    )


class SQEndpointForm(SQForm):

    def __init__(self, *args, **kwargs):
        super(SQEndpointForm, self).__init__(*args, **kwargs)
        self.fields['metric'].queryset = self.fields['metric'].queryset.filter(
            domain__assessment=self.instance.content_object.assessment)
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

        inputs["cancel_url"] = self.instance.content_object.get_absolute_url()

        helper = BaseFormHelper(self, **inputs)
        return helper

    def clean_metric(self):
        metric = self.cleaned_data['metric']
        qualities = self.instance.content_object.qualities.all()
        for quality in qualities:
            if metric == quality.metric and quality.id != self.instance.id:
                raise forms.ValidationError("Risk-of-bias metrics must be unique for a given endpoint.")
        return metric


class BaseSQFormSet(BaseModelFormSet):
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


class StudiesCopy(forms.Form):
    # TODO: remove study-type restriction

    HELP_TEXT = """
    Clone multiple studies and move from one assessment to  another assessment.
    Clones are complete and include most nested data.  Cloned studies do not
    include risk of bias information.
    """

    studies = forms.ModelMultipleChoiceField(
        queryset=models.Study.objects.all(),
        help_text="Select studies to copy (for now, epi-only).")
    assessment = forms.ModelChoiceField(
        queryset=Assessment.objects.all(),
        help_text="Select assessment you wish to copy these studies to.")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        assessment = kwargs.pop('assessment')
        super(StudiesCopy, self).__init__(*args, **kwargs)
        self.fields['assessment'].queryset = self.fields['assessment']\
            .queryset.model.get_editable_assessments(user, assessment.id)
        self.fields['studies'].queryset = self.fields['studies']\
            .queryset.filter(assessment_id=assessment.id, study_type=1)
        self.helper = self.setHelper(assessment)

    def setHelper(self, assessment):
        self.fields['studies'].widget.attrs['size'] = 15
        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span12'

        inputs = {
            "legend_text": "Copy studies across assessments",
            "help_text": self.HELP_TEXT,
            "cancel_url": reverse("study:list", args=[assessment.id]),
        }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper


SQFormSet = modelformset_factory(
    models.StudyQuality,
    form=SQForm,
    formset=BaseSQFormSet,
    extra=0)
