from django.shortcuts import get_object_or_404

from assessment.models import Assessment
from animal.models import Endpoint

from django.views.generic import RedirectView

from utils.views import BaseUpdate, BaseDetail, BaseDelete, \
    BaseList, ProjectManagerOrHigherMixin, TeamMemberOrHigherMixin

from . import forms, models


# Assessment settings
class AssessSettingsRead(BaseDetail):
    model = models.AssessmentSettings

    def get_object(self, **kwargs):
        # get the bmd settings of the specified assessment
        obj = get_object_or_404(self.model, assessment_id=self.kwargs['pk'])
        return super(AssessSettingsRead, self).get_object(object=obj, **kwargs)


class AssessSettingsUpdate(ProjectManagerOrHigherMixin, BaseUpdate):
    success_message = 'BMD Settings updated.'
    model = models.AssessmentSettings
    form_class = forms.AssessmentSettingsForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=kwargs['pk'])


class AssessLogicUpdate(ProjectManagerOrHigherMixin, BaseUpdate):
    success_message = 'BMD logic settings updated.'
    model = models.LogicField
    form_class = forms.LogicFieldForm

    def get_assessment(self, request, *args, **kwargs):
        return self.get_object().get_assessment()


# BMD sessions
class SessionCreate(TeamMemberOrHigherMixin, RedirectView):

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(Endpoint, pk=kwargs['pk'])
        return self.object.assessment

    def get_redirect_url(self, *args, **kwargs):
        obj = models.Session.create_new(self.object)
        return obj.get_update_url()


class SessionList(BaseList):
    parent_model = Endpoint
    model = models.Session
    parent_template_name = 'object'

    def get_queryset(self):
        return self.model.objects.filter(endpoint=self.parent)


class SessionDetail(BaseDetail):
    model = models.Session


class SessionUpdate(BaseUpdate):

    success_message = 'BMD session updated.'
    model = models.Session
    form_class = forms.SessionForm

    def get_redirect_url(self, *args, **kwargs):
        obj = models.Session.create_new(self.object)
        return obj.get_update_url()


class SessionDelete(BaseDelete):
    success_message = "BMD session deleted."
    model = models.Session

    def get_success_url(self):
        return self.object.endpoint.get_absolute_url()
