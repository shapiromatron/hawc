from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework import viewsets
from rest_framework import filters

from assessment.models import Assessment


class RequiresAssessmentID(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Please provide an `assessment_id` argument to your GET request.'


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


class InAssessmentFilter(filters.BaseFilterBackend):
    """
    Filter objects which are in a particular assessment.
    """
    def filter_queryset(self, request, queryset, view):
        if view.action != 'list':
            return queryset

        assessment_id = request.GET.get('assessment_id', None)
        if assessment_id is None:
            raise RequiresAssessmentID

        assessment = Assessment.objects.filter(id=assessment_id).first()
        if assessment and not assessment.user_can_view_object(request.user):
            raise PermissionDenied

        filters = {view.assessment_filter_args: assessment_id}
        return queryset.filter(**filters)


class AssessmentViewset(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions, )
    filter_backends = (InAssessmentFilter, )

    def get_queryset(self):
        return self.model.objects.all()
