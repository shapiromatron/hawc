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


class BMD_SessionForm(ModelForm):

    class Meta:
        model = models.BMD_session
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        kwargs.pop('parent', None)
        super(BMD_SessionForm, self).__init__(*args, **kwargs)
