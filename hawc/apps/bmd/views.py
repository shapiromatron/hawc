from functools import partialmethod

from django.core.exceptions import BadRequest, PermissionDenied
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView

from ..animal.models import Endpoint
from ..assessment.constants import AssessmentViewPermissions
from ..common.helper import WebappConfig
from ..common.views import BaseDelete, BaseDetail, BaseList
from . import models


# BMD sessions
class SessionCreate(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        self.object = get_object_or_404(Endpoint, pk=kwargs["pk"])
        if not self.object.assessment.user_can_edit_object(self.request.user):
            raise PermissionDenied()
        try:
            obj = models.Session.create_new(self.object)
        except ValueError as exc:
            raise BadRequest(
                "Assessment BMDS version is unsupported, can't create a new session."
            ) from exc
        return obj.get_update_url()


class SessionList(BaseList):
    parent_model = Endpoint
    model = models.Session
    parent_template_name = "object"

    def get_queryset(self):
        return super().get_queryset().filter(endpoint=self.parent)


def _get_session_config(self, context, is_editing: bool = False) -> WebappConfig:
    if self.object.is_bmds_version2():
        return WebappConfig(
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
    return WebappConfig(
        app="bmds3Startup",
        data=dict(
            edit=is_editing,
            session_url=self.object.get_api_url(),
            csrf=get_token(self.request) if is_editing else None,
        ),
    )


class SessionDetail(BaseDetail):
    model = models.Session
    get_app_config = partialmethod(_get_session_config, is_editing=False)


class SessionUpdate(BaseDetail):
    success_message = "BMD session updated."
    model = models.Session
    get_app_config = partialmethod(_get_session_config, is_editing=True)
    assessment_permission = AssessmentViewPermissions.TEAM_MEMBER_EDITABLE

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.object.is_bmds_version2():
            raise BadRequest(f"BMDS version {self.object.version} is unsupported, cannot update.")
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
