from django.db.models import prefetch_related_objects
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentLevelPermissions,
    DisabledPagination,
    InAssessmentFilter,
    get_assessment_id_param,
)
from ..common.api import CleanupFieldsBaseViewSet
from ..common.helper import re_digits
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
        cls = serializers.VerboseStudySerializer
        if self.action == "list":
            cls = serializers.SimpleStudySerializer
        elif self.action == "create":
            cls = serializers.SimpleStudySerializer
        return cls

    def get_queryset(self):
        if self.action == "list":
            if not self.assessment.user_can_edit_object(self.request.user):
                return self.model.objects.published(self.assessment)
            return self.model.objects.get_qs(self.assessment)
        else:
            return self.model.objects.prefetch_related(
                "identifiers", "riskofbiases__scores__metric__domain",
            ).select_related("assessment__rob_settings", "assessment")

    @action(detail=False)
    def rob_scores(self, request):
        assessment_id = get_assessment_id_param(request)
        scores = self.model.objects.rob_scores(assessment_id)
        return Response(scores)

    @action(detail=False)
    def types(self, request):
        study_types = self.model.STUDY_TYPE_FIELDS
        return Response(study_types)

    @action(detail=True)
    def v2(self, request, pk):
        # TODO - fix ROB June 2021  (replace StudySerializer->NewStudySerializer; switch api)
        instance = self.get_object()
        prefetch_related_objects([instance], "riskofbiases__scores__overridden_objects")
        ser = serializers.NewStudySerializer(instance)
        return Response(ser.data)

    def create(self, request):
        # permissions check not here; see serializer validation
        return super().create(request)


class StudyCleanupFieldsView(CleanupFieldsBaseViewSet):
    model = models.Study
    serializer_class = serializers.StudyCleanupFieldsSerializer
    assessment_filter_args = "assessment"
