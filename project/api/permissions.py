from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.response import Response
from rest_framework import viewsets

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


class AssessmentViewset(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = ""
    permission_classes = (AssessmentLevelPermissions, )

    def list(self, request):
        # override list to only return meta-results for a single assessment
        filters = {self.assessment_filter_args: get_permitted_assessment(request)}
        by_assessment = self.model.objects.filter(**filters)
        page = self.paginate_queryset(by_assessment)
        serializer = self.get_pagination_serializer(page)
        return Response(serializer.data)

    def get_queryset(self):
        return self.model.objects.all()

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
