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
