from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from ..animal.models import Endpoint
from ..assessment.models import Assessment
from ..common.helper import WebappConfig
from ..common.views import (
    BaseDelete,
    BaseDetail,
    BaseList,
    BaseUpdate,
    ProjectManagerOrHigherMixin,
    TeamMemberOrHigherMixin,
)
from . import forms, models


# Assessment settings
class AssessSettingsRead(BaseDetail):
    model = models.AssessmentSettings

    def get_object(self, **kwargs):
        # get the bmd settings of the specified assessment
        obj = get_object_or_404(self.model, assessment_id=self.kwargs["pk"])
        return super(AssessSettingsRead, self).get_object(object=obj, **kwargs)


class AssessSettingsUpdate(ProjectManagerOrHigherMixin, BaseUpdate):
    success_message = "BMD Settings updated."
    model = models.AssessmentSettings
    form_class = forms.AssessmentSettingsForm

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=kwargs["pk"])


class AssessLogicUpdate(ProjectManagerOrHigherMixin, BaseUpdate):
    success_message = "BMD logic settings updated."
    model = models.LogicField
    form_class = forms.LogicFieldForm

    def get_assessment(self, request, *args, **kwargs):
        return self.get_object().get_assessment()


# BMD sessions
class SessionCreate(TeamMemberOrHigherMixin, RedirectView):
    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(Endpoint, pk=kwargs["pk"])
        return self.object.assessment

    def get_redirect_url(self, *args, **kwargs):
        obj = models.Session.create_new(self.object)
        return obj.get_update_url()


class SessionList(BaseList):
    parent_model = Endpoint
    model = models.Session
    parent_template_name = "object"

    def get_queryset(self):
        return self.model.objects.filter(endpoint=self.parent)


def _get_session_config(view, context) -> WebappConfig:
    edit_mode = view.crud == "Update"
    return WebappConfig(
        app="bmds2Startup",
        data=dict(
            editMode=edit_mode,
            assessment_id=view.assessment.id,
            bmds_version=view.object.get_version_display(),
            endpoint_id=view.object.endpoint_id,
            session_url=view.object.get_api_url(),
            execute_url=view.object.get_execute_url(),
            execute_status_url=view.object.get_execute_status_url(),
            selected_model_url=view.object.get_selected_model_url(),
            csrf=get_token(view.request) if edit_mode else None,
        ),
    )


class SessionDetail(BaseDetail):
    model = models.Session
    get_app_config = _get_session_config


class SessionUpdate(BaseUpdate):

    success_message = "BMD session updated."
    model = models.Session
    form_class = forms.SessionForm
    get_app_config = _get_session_config

    def get_redirect_url(self, *args, **kwargs):
        obj = models.Session.create_new(self.object)
        return obj.get_update_url()


class SessionDelete(BaseDelete):
    success_message = "BMD session deleted."
    model = models.Session
    get_app_config = _get_session_config

    def get_success_url(self):
        return self.object.endpoint.get_absolute_url()
