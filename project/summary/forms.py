from django import forms
from django.core.urlresolvers import reverse
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
        exclude = ('assessment', 'visual_type', 'prefilters')

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
                    Create a custom-visualization.
                    Generally, you will select a subset of available data on the
                    "Data" tab, then will customize the visualization using the
                    "Settings" tab. To view a preview of the visual at any time,
                    select the "Preview" tab.
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
        exclude = ('assessment', 'visual_type', 'prefilters', 'studies')


class CrossviewForm(VisualForm):

    published_only = forms.BooleanField(
        required=False,
        initial=True,
        label="Published studies only",
        help_text='Only present data from studies which have been marked as '
                  '"published" in HAWC.')

    prefilter_system = forms.BooleanField(
        required=False,
        label="Prefilter by system",
        help_text="Prefilter endpoints on plot to include on select systems.")

    systems = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        label="Systems to include",
        help_text="""Select one or more systems to include in the plot.
                     If no system is selected, no endpoints will be available.""")

    prefilter_effect = forms.BooleanField(
        required=False,
        label="Prefilter by effect",
        help_text="Use this box to limit the effects.")

    effects = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        label="Effects to include",
        help_text="""Select one or more effects to include in the plot.
                     If no effect is selected, no endpoints will be available.""")

    def __init__(self, *args, **kwargs):
        super(CrossviewForm, self).__init__(*args, **kwargs)

        self.pf = models.Prefilter(self)
        self.pf.setInitialForm()

        self.fields["prefilters"].widget = forms.HiddenInput()
        self.fields["systems"].choices = self.pf.getChoices("systems")
        self.fields["effects"].choices = self.pf.getChoices("effects")

        self.fields["systems"].widget.attrs['size'] = 10
        self.fields["effects"].widget.attrs['size'] = 10

    def clean(self):
        cleaned_data = super(CrossviewForm, self).clean()
        cleaned_data["prefilters"] = self.pf.setPrefilters(cleaned_data)
        return cleaned_data

    class Meta:
        model = models.Visual
        exclude = ('assessment', 'visual_type', 'endpoints', 'studies')


class RoBForm(VisualForm):

    prefilter_system = forms.BooleanField(
        required=False,
        label="Prefilter studies by system",
        help_text="""Only studies which report Endpoints with the selected system(s) will be presented.""")

    systems = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        label="Systems to include",
        help_text="""Select one or more systems to include.
                     If no system is selected, no studies will be available.""")

    prefilter_effect = forms.BooleanField(
        required=False,
        label="Prefilter by effect",
        help_text="""Only studies which report Endpoints with the selected effect(s) will be presented.""")

    effects = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        label="Effects to include",
        help_text="""Select one or more effects to include.
                     If no effect is selected, no studies will be available.""")

    def __init__(self, *args, **kwargs):
        super(RoBForm, self).__init__(*args, **kwargs)
        self.fields["studies"].queryset = \
            self.fields["studies"]\
                .queryset\
                .filter(assessment=self.instance.assessment)

        self.pf = models.Prefilter(self)
        self.pf.setInitialForm()

        self.fields["prefilters"].widget = forms.HiddenInput()
        self.fields["systems"].choices = self.pf.getChoices("systems")
        self.fields["effects"].choices = self.pf.getChoices("effects")

        self.fields["studies"].widget.attrs['size'] = 10
        self.fields["systems"].widget.attrs['size'] = 10
        self.fields["effects"].widget.attrs['size'] = 10

    def clean(self):
        cleaned_data = super(RoBForm, self).clean()
        cleaned_data["prefilters"] = self.pf.setPrefilters(cleaned_data)
        return cleaned_data

    class Meta:
        model = models.Visual
        exclude = ('assessment', 'visual_type', 'dose_units', 'endpoints')


def get_visual_form(visual_type):
    try:
        return {
            0: EndpointAggregationForm,
            1: CrossviewForm,
            2: RoBForm,
            3: RoBForm
        }[visual_type]
    except:
        raise ValueError()


class DataPivotForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        assessment = kwargs.pop('parent', None)
        super(DataPivotForm, self).__init__(*args, **kwargs)
        if assessment:
            self.instance.assessment = assessment
        self.helper = self.setHelper()
        self.fields['settings'].widget.attrs['rows'] = 2

    def setHelper(self):

        for fld in self.fields.keys():
            widget = self.fields[fld].widget
            if type(widget) != forms.CheckboxInput:
                widget.attrs['class'] = 'span12'

        if self.instance.id:
            inputs = {
                "legend_text": u"Update {}".format(self.instance),
                "help_text":   u"Update an existing data-pivot.",
                "cancel_url": self.instance.get_absolute_url()
            }
        else:
            inputs = {
                "legend_text": u"Create new data-pivot",
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


class DataPivotUploadForm(DataPivotForm):

    class Meta:
        model = models.DataPivotUpload
        exclude = ('assessment', )

    def __init__(self, *args, **kwargs):
        super(DataPivotUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'].help_text += """<br>
            For more details on saving in this format from Excel,
            <a href="{0}" target="_blank">click here</a>.
            """.format(reverse('summary:dp_excel-unicode'))


class DataPivotQueryForm(DataPivotForm):

    prefilter_system = forms.BooleanField(
        required=False,
        label="Prefilter by system",
        help_text="Prefilter endpoints on plot to include on select systems.")

    systems = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        label="Systems to include",
        help_text="""Select one or more systems to include in the plot.
                     If no system is selected, no endpoints will be available.""")

    prefilter_effect = forms.BooleanField(
        required=False,
        label="Prefilter by effect",
        help_text="Use this box to limit the effects.")

    effects = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple,
        label="Effects to include",
        help_text="""Select one or more effects to include in the plot.
                     If no effect is selected, no endpoints will be available.""")
    class Meta:
        model = models.DataPivotQuery
        fields =('evidence_type', 'units', 'title',
                 'slug', 'settings', 'caption',
                 'published_only', 'prefilters')

    def __init__(self, *args, **kwargs):
        super(DataPivotQueryForm, self).__init__(*args, **kwargs)
        self.fields["evidence_type"].choices = (
            (0, 'Animal Bioassay'),
            (1, 'Epidemiology'),
            (4, 'Epidemiology meta-analysis/pooled analysis'),
            (2, 'In vitro'))

        self.pf = models.Prefilter(self)
        self.pf.setInitialForm()

        self.fields["prefilters"].widget = forms.HiddenInput()
        self.fields["systems"].choices = self.pf.getChoices("systems")
        self.fields["effects"].choices = self.pf.getChoices("effects")

        self.fields["systems"].widget.attrs['size'] = 10
        self.fields["effects"].widget.attrs['size'] = 10

    def clean(self):
        cleaned_data = super(DataPivotQueryForm, self).clean()
        cleaned_data["prefilters"] = self.pf.setPrefilters(cleaned_data)
        return cleaned_data


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
