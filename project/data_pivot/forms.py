from django import forms

from assessment.models import Assessment

from . import models


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
            self.fields["evidence_type"].choices = ((0, 'Animal Bioassay'),
                                                    (1, 'Epidemiology'))
            if assessment:
                self.instance.assessment = assessment


class DataPivotSettingsForm(forms.ModelForm):

    class Meta:
        model = models.DataPivot
        fields = ('settings', )


class DataPivotSearchForm(forms.Form):
    title = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        assessment_pk = kwargs.pop('assessment_pk', None)
        super(DataPivotSearchForm, self).__init__(*args, **kwargs)
        if assessment_pk:
            self.assessment = Assessment.objects.get(pk=assessment_pk)

    def search(self):
        response_json = []
        query = {'assessment': self.assessment,
                 'title__icontains': self.cleaned_data['title']}
        for obj in models.DataPivot.objects.filter(**query):
            response_json.append(obj.get_json(json_encode=False))
        return response_json
