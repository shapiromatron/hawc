from rest_framework import permissions

"""
Also note that the generic views will only check the object-level permissions
for views that retrieve a single model instance. If you require object-level
filtering of list views, you'll need to filter the queryset separately.
See the filtering documentation for more details.
"""

class AssesssmentLevelPermissions(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        assessment = obj.get_assessment()

        # (GET, HEAD or OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return assessment.user_can_view_object(request.user)

        # (POST, PUT, DELETE)
        if obj == assessment:
            return assessment.user_can_edit_assessment(request.user)
        else:
            return assessment.user_can_edit_object(request.user)
