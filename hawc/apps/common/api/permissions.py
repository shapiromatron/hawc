import logging

from django.db import models
from rest_framework import exceptions, permissions

from ...assessment.api.helper import get_assessment_from_query
from ..constants import AssessmentViewsetPermissions

logger = logging.getLogger(__name__)


def user_can_edit_object(
    instance: models.Model, user: models.Model, raise_exception: bool = False
) -> bool:
    """Permissions check to ensure that user can edit assessment objects

    Args:
        instance (models.Model): The instance to check
        user (models.Model): The user instance
        raise_exception (bool, optional): Throw an Exception; defaults to False.

    Raises:
        exceptions.PermissionDenied: If raise_exc is True and user doesn't have permission

    """
    can_edit = instance.get_assessment().user_can_edit_object(user)
    if raise_exception and not can_edit:
        raise exceptions.PermissionDenied("Invalid permission to edit assessment.")
    return can_edit


class CleanupFieldsPermissions(permissions.BasePermission):
    """
    Custom permissions for bulk-cleanup view. No object-level permissions. Here we check that
    the user has permission to edit content for this assessment, but not necessarily that they
    can edit the specific ids selected.
    """

    def has_object_permission(self, request, view, obj):
        # no object-specific permissions
        return False

    def has_permission(self, request, view):
        # must be team-member or higher to bulk-edit
        view.assessment = get_assessment_from_query(request)
        return view.assessment.user_can_edit_object(request.user)


class AssessmentLevelPermissions(permissions.BasePermission):
    default_list_actions = ["list"]
    default_action_perms = {
        "retrieve": AssessmentViewsetPermissions.CAN_VIEW_OBJECT,
        "list": AssessmentViewsetPermissions.CAN_VIEW_OBJECT,
        "create": AssessmentViewsetPermissions.CAN_EDIT_OBJECT,
        "update": AssessmentViewsetPermissions.CAN_EDIT_OBJECT,
        "partial_update": AssessmentViewsetPermissions.CAN_EDIT_OBJECT,
        "destroy": AssessmentViewsetPermissions.CAN_EDIT_OBJECT,
        "metadata": AssessmentViewsetPermissions.CAN_VIEW_OBJECT,
    }

    def fix_view_action(self, request, view):
        """
        BrowsableAPIRenderer (ie the renderer used when DEBUG=TRUE) interacts directly with the
        view when building its forms, and in the process overrides view.action with None on
        its OPTIONS requests.

        BrowsableAPIRenderer calls override_method:
        https://github.com/encode/django-rest-framework/blob/bfce663a604bf9d2c891ab2414fee0e59cabeb46/rest_framework/renderers.py#L474
        which uses view.action_map to set view.action:
        https://github.com/encode/django-rest-framework/blob/bfce663a604bf9d2c891ab2414fee0e59cabeb46/rest_framework/request.py#L55
        but OPTIONS isn't included in the mapping on default routes (ie view.action_map):
        https://github.com/encode/django-rest-framework/blob/bfce663a604bf9d2c891ab2414fee0e59cabeb46/rest_framework/routers.py#L95-L136

        The action for OPTIONS requests is instead added explicitly and by default when the request is initialized:
        https://github.com/encode/django-rest-framework/blob/bfce663a604bf9d2c891ab2414fee0e59cabeb46/rest_framework/viewsets.py#L148-L152

        The fix is to explicitly set the view.action once again if it is None and the method is OPTIONS.
        """
        if view.action is None and request.method == "OPTIONS":
            view.action = "metadata"

    def assessment_permission(self, view):
        action_perms = getattr(view, "action_perms", {})
        if isinstance(action_perms, dict):
            action_perms = dict(self.default_action_perms, **action_perms)
            assessment_permission = action_perms[view.action]
        else:
            assessment_permission = action_perms
        return assessment_permission

    def has_object_permission(self, request, view, obj):
        if not hasattr(view, "assessment"):
            view.assessment = obj.get_assessment()
        return self.assessment_permission(view).has_permission(view.assessment, request.user)

    def has_permission(self, request, view):
        self.fix_view_action(request, view)

        list_actions = getattr(view, "list_actions", self.default_list_actions)
        if view.action in list_actions:
            logger.debug("Permission checked")

            if not hasattr(view, "assessment"):
                view.assessment = get_assessment_from_query(request)

            return self.assessment_permission(view).has_permission(view.assessment, request.user)

        return True


class AssessmentReadPermissions(AssessmentLevelPermissions):
    def has_object_permission(self, request, view, obj):
        if not hasattr(view, "assessment"):
            view.assessment = obj.get_assessment()
        return view.assessment.user_can_view_object(request.user)
