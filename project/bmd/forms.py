from django.forms import ModelForm, HiddenInput

from . import models


class AssessmentSettingsForm(ModelForm):

    class Meta:
        model = models.BMD_Assessment_Settings
        exclude = ('assessment', )


class LogicFieldForm(ModelForm):

    class Meta:
        model = models.LogicField
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LogicFieldForm, self).__init__(*args, **kwargs)
        if self.instance.threshold is None:
            self.fields.pop('threshold')


class BMDSessionForm(ModelForm):

    class Meta:
        model = models.BMDSession
        fields = '__all__'
