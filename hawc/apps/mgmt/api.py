from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import AssessmentEditViewset, AssessmentLevelPermissions
from ..common.api import DisabledPagination
from ..common.constants import AssessmentViewsetPermissions
from . import models, serializers


class TaskViewSet(AssessmentEditViewset):
    http_method_names = ["get", "patch", "head", "options", "trace"]
    assessment_filter_args = "study__assessment"
    model = models.Task
    list_actions = ["list", "assessment_assignments"]
    serializer_class = serializers.TaskSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        AssessmentLevelPermissions,
    )
    pagination_class = DisabledPagination

    def get_queryset(self):
        return super().get_queryset().select_related("owner", "study", "study__assessment")

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def assignments(self, request):
        # Tasks assigned to user.
        qs = self.model.objects.owned_by(request.user).select_related(
            "owner", "study", "study__reference_ptr", "study__assessment"
        )
        serializer = serializers.TaskByAssessmentSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, action_perms=AssessmentViewsetPermissions.CAN_VIEW_OBJECT)
    def assessment_assignments(self, request):
        # Tasks assigned to user for a specific assessment
        qs = (
            self.model.objects.owned_by(request.user)
            .filter(study__assessment=self.assessment)
            .select_related("owner", "study", "study__reference_ptr", "study__assessment")
        )
        serializer = serializers.TaskByAssessmentSerializer(qs, many=True)
        return Response(serializer.data)
