from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentLevelPermissions,
    DisabledPagination,
    InAssessmentFilter,
    get_assessment_id_param,
)
from ..common.api import CleanupFieldsBaseViewSet
from ..common.helper import re_digits
from ..riskofbias.serializers import RiskOfBiasSerializer
from . import models, serializers


class Study(
    mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet,
):
    assessment_filter_args = "assessment"
    model = models.Study
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, DjangoFilterBackend)
    list_actions = ["list", "rob_scores"]
    lookup_value_regex = re_digits

    def get_serializer_class(self):
        if self.action in ["list", "create"]:
            return serializers.SimpleStudySerializer
        else:
            return serializers.VerboseStudySerializer

    def get_queryset(self):
        if self.action == "list":
            if not self.assessment.user_can_edit_object(self.request.user):
                return self.model.objects.published(self.assessment)
            return self.model.objects.get_qs(self.assessment)
        else:
            return self.model.objects.prefetch_related("identifiers").select_related("assessment")

    @action(detail=False)
    def rob_scores(self, request):
        assessment_id = get_assessment_id_param(request)
        scores = self.model.objects.rob_scores(assessment_id)
        return Response(scores)

    @action(detail=False)
    def types(self, request):
        study_types = self.model.STUDY_TYPE_FIELDS
        return Response(study_types)

    def create(self, request):
        # permissions check not here; see serializer validation
        return super().create(request)

    @action(detail=True, url_path="all-rob")
    def rob(self, request, pk: int):
        study = self.get_object()
        if not self.assessment.user_is_team_member_or_higher(self.request.user):
            raise PermissionDenied("You must be part of the team to view unpublished data")
        serializer = RiskOfBiasSerializer(study.get_active_robs(), many=True)
        return Response(serializer.data)


class StudyCleanupFieldsView(CleanupFieldsBaseViewSet):
    model = models.Study
    serializer_class = serializers.StudyCleanupFieldsSerializer
    assessment_filter_args = "assessment"
