from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework import permissions

from assessment.api import AssessmentEditViewset, AssessmentLevelPermissions, \
    DisabledPagination

from . import models, serializers


class Task(AssessmentEditViewset):
    assessment_filter_args = "study__assessment"
    model = models.Task
    serializer_class = serializers.TaskSerializer
    permission_classes = (AssessmentLevelPermissions, permissions.IsAuthenticated, )
    pagination_class = DisabledPagination
    list_actions = ['list', 'dashboard']

    def filter_queryset(self, queryset):
        return super(Task, self)\
            .filter_queryset(queryset)\
            .select_related('owner', 'study')

    @list_route()
    def assignments(self, request):
        # Tasks assigned to user.
        qs = self.model.objects\
            .owned_by(request.user)\
            .select_related('owner', 'study', 'study__reference_ptr', 'study__assessment')
        serializer = serializers.TaskByAssessmentSerializer(qs, many=True)
        return Response(serializer.data)

    @list_route()
    def dashboard(self, request):
        qs = self.filter_queryset(self.get_queryset())
        metrics = self.model.dashboard_metrics(qs)
        return Response(metrics)
