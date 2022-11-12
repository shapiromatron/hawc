import logging

from django.db import models
from rest_framework import exceptions, permissions

from ...assessment.api import get_assessment_from_query

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


# TODO
# https://stackoverflow.com/questions/67153946/
class AssessmentLevelPermissions(permissions.BasePermission):
    default_list_actions = ["list"]

    def has_object_permission(self, request, view, obj):
        if not hasattr(view, "assessment"):
            view.assessment = obj.get_assessment()
        if request.method in permissions.SAFE_METHODS:
            return view.assessment.user_can_view_object(request.user)
        elif obj == view.assessment:
            return view.assessment.user_can_edit_assessment(request.user)
        else:
            return view.assessment.user_can_edit_object(request.user)

    def has_permission(self, request, view):
        list_actions = getattr(view, "list_actions", self.default_list_actions)
        if view.action in list_actions:
            logger.debug("Permission checked")

            if not hasattr(view, "assessment"):
                view.assessment = get_assessment_from_query(request)

            return view.assessment.user_can_view_object(request.user)

        return True


class AssessmentReadPermissions(AssessmentLevelPermissions):
    def has_object_permission(self, request, view, obj):
        if not hasattr(view, "assessment"):
            view.assessment = obj.get_assessment()
        return view.assessment.user_can_view_object(request.user)
