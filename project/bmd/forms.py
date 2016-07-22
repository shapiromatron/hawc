from django.forms import ModelForm

from . import models


class AssessmentSettingsForm(ModelForm):

    class Meta:
        model = models.AssessmentSettings
        exclude = ('assessment', )


class LogicFieldForm(ModelForm):

    class Meta:
        model = models.LogicField
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LogicFieldForm, self).__init__(*args, **kwargs)
        if self.instance.threshold is None:
            self.fields.pop('threshold')


class SessionForm(ModelForm):

    class Meta:
        model = models.Session
        fields = '__all__'
