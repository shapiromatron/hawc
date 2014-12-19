from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, APIException

from assessment.models import Assessment


class RequiresAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Please provide an `assessment_id` argument to your GET request.'


def get_permitted_assessment(request):
    # Used for determining if a user has access to view assessment-view.
    # First, check if assessment is specified. If not, raise RequiresAssessmentID
    # Then, check if user has permission to view. If not, raise 403
    assessment_id = request.GET.get('assessment_id')
    if assessment_id is None:
        raise RequiresAssessmentID
    assessment = Assessment.objects.filter(id=assessment_id).first()
    if assessment and not assessment.user_can_view_object(request.user):
        raise PermissionDenied
    return assessment


class AssessmentLevelPermissions(permissions.BasePermission):

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
