from json import dumps

from django.shortcuts import HttpResponse, get_object_or_404

from assessment.models import Assessment
from utils.views import BaseUpdate, BaseDetail, \
    ProjectManagerOrHigherMixin

from . import forms, models


# Assessment settings
class AssessSettingsRead(BaseDetail):
    model = models.BMD_Assessment_Settings


class AssessSettingsUpdate(ProjectManagerOrHigherMixin, BaseUpdate):
    success_message = 'BMD Settings updated.'
    model = models.BMD_Assessment_Settings
    form_class = forms.AssessmentSettingsForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=kwargs['pk'])


class AssessLogicUpdate(ProjectManagerOrHigherMixin, BaseUpdate):
    success_message = 'BMD Logic Settings updated.'
    model = models.LogicField
    form_class = forms.LogicFieldForm

    def get_assessment(self, request, *args, **kwargs):
        return self.get_object().get_assessment()

    """
    Return json object for the default model options for a given model_type and
    BMDS version.
    """
    def get(self, request, *args, **kwargs):
        try:
            version = BMDS.versions[str(self.kwargs['vbmds'])]
            run_instance = version.models[
                self.kwargs['datatype']][self.kwargs['model_name']]()
            model_data = models.BMD_model_run.get_model_template(
                self.kwargs['model_name'], run_instance)
        except:
            model_data = {'error': 'No BMDS models meet this description.'}
        return HttpResponse(dumps(model_data), content_type="application/json")
