from rest_framework import permissions


class JobPermissions(permissions.BasePermission):
    """
    Requires admin permissions where jobs have no associated assessment
    or when part of a list, and assessment level permissions when jobs
    have an associated assessment.
    """

    def has_object_permission(self, request, view, obj):
        if obj.assessment is None:
            return bool(request.user and request.user.is_staff)
        elif request.method in permissions.SAFE_METHODS:
            return obj.assessment.user_can_view_object(request.user)
        else:
            return obj.assessment.user_can_edit_object(request.user)

    def has_permission(self, request, view):
        if view.action == "list":
            return bool(request.user and request.user.is_staff)
        elif view.action == "create":
            serializer = view.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            assessment = serializer.validated_data.get("assessment")
            if assessment is None:
                return bool(request.user and request.user.is_staff)
            else:
                return assessment.user_can_edit_object(request.user)
        else:
            # other actions are object specific,
            # and will be caught by object permissions
            return True
