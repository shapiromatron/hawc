from django import forms
from selectable import forms as selectable

from animal.lookups import EndpointByAssessmentLookup
from assessment.models import Assessment
from utils.forms import BaseFormHelper

from . import models



class SummaryTextForm(forms.ModelForm):

    delete = forms.BooleanField(initial=False)
    parent = forms.ChoiceField(choices=(), required=True)
    sibling = forms.ChoiceField(label="Insert After", choices=(), required=True)
    id = forms.IntegerField()

    class Meta:
        model = models.SummaryText
        fields = ('title', 'slug', 'text', )

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent')
        assessment_pk = kwargs.pop('assessment_pk', None)
        super(SummaryTextForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['rows'] = 30
        if assessment_pk:
            self.instance.assessment = Assessment.objects.get(pk=assessment_pk)
        self.fields.keyOrder = ['delete', 'id', 'parent',
                                'sibling', 'title', 'slug', 'text']


class VisualForm(forms.ModelForm):

    class Meta:
        model = models.Visual
        exclude = ('assessment', 'visual_type')

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        visual_type = kwargs.pop('visual_type', None)
        super(VisualForm, self).__init__(*args, **kwargs)
        self.fields['settings'].widget.attrs['rows'] = 2
        if assessment:
            self.instance.assessment = assessment
        if visual_type is not None:  # required if value is 0
            self.instance.visual_type = visual_type
        self.helper = self.setHelper()

    def setHelper(self):

        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   u"Update an existing visualization.",
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new visualization",
                "help_text":   u"""
                    Create a custom-visualization for this assessment.
                    Generally, you will select a subset of available data, then
                    customize the visualization the next-page.
                """,
                "cancel_url": self.instance.get_list_url(self.instance.assessment.id)
            }

        helper = BaseFormHelper(self, **inputs)
        helper.form_class = None
        return helper


class EndpointAggregationForm(VisualForm):

    def __init__(self, *args, **kwargs):
        super(EndpointAggregationForm, self).__init__(*args, **kwargs)
        self.fields["endpoints"] = selectable.AutoCompleteSelectMultipleField(
            lookup_class=EndpointByAssessmentLookup,
            label='Endpoints',
            widget=selectable.AutoCompleteSelectMultipleWidget)
        self.fields["endpoints"].widget.update_query_parameters(
            {'assessment_id': self.instance.assessment_id})
        self.helper = self.setHelper()

    class Meta:
        model = models.Visual
        exclude = ('assessment', 'visual_type')


class CrossviewForm(VisualForm):

    class Meta:
        model = models.Visual
        exclude = ('assessment', 'visual_type', 'endpoints')


def get_visual_form(visual_type):
    try:
        return {
            0: EndpointAggregationForm,
            1: CrossviewForm
        }[visual_type]
    except:
        raise ValueError()


class DataPivotUploadForm(forms.ModelForm):

    class Meta:
        model = models.DataPivotUpload
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(DataPivotUploadForm, self).__init__(*args, **kwargs)
        self.fields['settings'].widget.attrs['rows'] = 2
        if assessment:
            self.instance.assessment = assessment


class DataPivotQueryForm(forms.ModelForm):

    class Meta:
        model = models.DataPivotQuery
        fields =('evidence_type', 'units', 'title', 'slug',
                 'settings', 'caption')

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(DataPivotQueryForm, self).__init__(*args, **kwargs)
        self.fields['settings'].widget.attrs['rows'] = 2
        self.fields["evidence_type"].choices = (
            (0, 'Animal Bioassay'),
            (1, 'Epidemiology'),
            (4, 'Epidemiology meta-analysis/pooled analysis'),
            (2, 'In vitro'))
        if assessment:
            self.instance.assessment = assessment


class DataPivotSettingsForm(forms.ModelForm):

    class Meta:
        model = models.DataPivot
        fields = ('settings', )


class DataPivotSearchForm(forms.Form):
    title = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop('assessment', None)
        super(DataPivotSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        response_json = []
        query = {'assessment': self.assessment,
                 'title__icontains': self.cleaned_data['title']}
        for obj in models.DataPivot.objects.filter(**query):
            response_json.append(obj.get_json(json_encode=False))
        return response_json


class DataPivotSelectorForm(forms.Form):

    dp = forms.ModelChoiceField(label="Data Pivot",
                                queryset=models.DataPivot.objects.all(),
                                empty_label=None)

    def __init__(self, *args, **kwargs):
        assessment_id = kwargs.pop('assessment_id', -1)
        super(DataPivotSelectorForm, self).__init__(*args, **kwargs)

        for fld in self.fields.keys():
            self.fields[fld].widget.attrs['class'] = 'span12'

        self.fields['dp'].queryset = self.fields['dp'].queryset.filter(assessment_id = assessment_id)
