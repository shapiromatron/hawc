from functools import partialmethod

from django.core.exceptions import BadRequest
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
        return super().get_object(object=obj, **kwargs)


class AssessSettingsUpdate(ProjectManagerOrHigherMixin, BaseUpdate):
    success_message = "BMD Settings updated."
    model = models.AssessmentSettings
    form_class = forms.AssessmentSettingsForm

    def get_object(self, **kwargs):
        # get the bmd settings of the specified assessment
        obj = get_object_or_404(self.model, assessment_id=self.kwargs["pk"])
        return super().get_object(object=obj, **kwargs)

    def get_assessment(self, request, *args, **kwargs):
        return get_object_or_404(Assessment, pk=kwargs["pk"])


# BMD sessions
class SessionCreate(TeamMemberOrHigherMixin, RedirectView):
    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(Endpoint, pk=kwargs["pk"])
        return self.object.assessment

    def get_redirect_url(self, *args, **kwargs):
        try:
            obj = models.Session.create_new(self.object)
        except ValueError:
            raise BadRequest("Assessment BMDS version is unsupported, can't create a new session.")
        return obj.get_update_url()


class SessionList(BaseList):
    parent_model = Endpoint
    model = models.Session
    parent_template_name = "object"

    def get_queryset(self):
        return self.model.objects.filter(endpoint=self.parent)


def _get_session_config(self, context, is_editing: bool = False) -> WebappConfig:
    if self.object.can_edit:
        config = WebappConfig(
            app="bmds3Startup",
            data=dict(
                edit=is_editing,
                session_url=self.object.get_api_url(),
                csrf=get_token(self.request) if is_editing else None,
            ),
        )
    else:
        config = WebappConfig(
            app="bmds2Startup",
            data=dict(
                editMode=is_editing,
                assessment_id=self.assessment.id,
                bmds_version=self.object.get_version_display(),
                endpoint_id=self.object.endpoint_id,
                session_url=self.object.get_api_url(),
                csrf=get_token(self.request) if is_editing else None,
            ),
        )
    return config


class SessionDetail(BaseDetail):
    model = models.Session
    get_app_config = partialmethod(_get_session_config, is_editing=False)


class SessionUpdate(TeamMemberOrHigherMixin, BaseDetail):
    success_message = "BMD session updated."
    model = models.Session
    get_app_config = partialmethod(_get_session_config, is_editing=True)

    def get_assessment(self, request, *args, **kwargs):
        self.object = get_object_or_404(models.Session, pk=kwargs["pk"])
        return self.object.get_assessment()

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not self.object.can_edit:
            raise BadRequest("Session BMDS version is unsupported, can't update this session.")
        return response

    def get_redirect_url(self, *args, **kwargs):
        obj = models.Session.create_new(self.object)
        return obj.get_update_url()


class SessionDelete(BaseDelete):
    success_message = "BMD session deleted."
    model = models.Session
    get_app_config = partialmethod(_get_session_config, is_editing=False)

    def get_success_url(self):
        return self.object.endpoint.get_absolute_url()
