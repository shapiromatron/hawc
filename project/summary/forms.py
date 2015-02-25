from django import forms

from assessment.models import Assessment

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
