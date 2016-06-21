from django.forms import ModelForm

from . import models


class AssessmentSettingsForm(ModelForm):

    class Meta:
        model = models.BMD_Assessment_Settings
        exclude = ('assessment', )


class LogicFieldForm(ModelForm):
    # TODO: if default threshold is blank, don't display field,
    # otherwise make required

    class Meta:
        model = models.LogicField
        fields = '__all__'


class BMDSessionForm(ModelForm):
    class Meta:
        model = models.BMDSession
        fields = '__all__'
