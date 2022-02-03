from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import AssessmentEditViewset, AssessmentLevelPermissions, DisabledPagination
from ..assessment.models import Assessment
from . import models, serializers


class TaskViewSet(AssessmentEditViewset):
    http_method_names = ["get", "post", "patch", "head", "options", "trace"]
    assessment_filter_args = "study__assessment"
    model = models.Task
    serializer_class = serializers.TaskSerializer
    permission_classes = (
        AssessmentLevelPermissions,
        permissions.IsAuthenticated,
    )
    pagination_class = DisabledPagination
    list_actions = ["list", "bulk_patch"]

    def get_queryset(self):
        return super().get_queryset().select_related("owner", "study", "study__assessment")

    @action(detail=False)
    def assignments(self, request):
        # Tasks assigned to user.
        qs = self.model.objects.owned_by(request.user).select_related(
            "owner", "study", "study__reference_ptr", "study__assessment"
        )
        serializer = serializers.TaskByAssessmentSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def assessment_assignments(self, request, pk=None):
        # Tasks assigned to user for a specific assessment
        assessment = get_object_or_404(Assessment, pk=pk)
        qs = (
            self.model.objects.owned_by(request.user)
            .filter(study__assessment=assessment)
            .select_related("owner", "study", "study__reference_ptr", "study__assessment")
        )
        serializer = serializers.TaskByAssessmentSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=("patch",))
    def bulk_patch(self, request):
        qs = self.filter_queryset(self.get_queryset())
        # ensure high-level validation passes
        serializer = self.get_serializer(data=request.data, partial=True, many=True)
        serializer.is_valid(raise_exception=True)
        # try to bulk-update; return new queryset
        qs = self.model.objects.update_many(self.assessment, request.data)
        # return response with new values
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)
