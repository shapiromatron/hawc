from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from ..assessment.api import AssessmentLevelPermissions, DisabledPagination, InAssessmentFilter
from ..common.api import CleanupFieldsBaseViewSet
from ..common.helper import tryParseInt
from ..lit.models import Reference
from . import models, serializers


class Study(
    viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin,
):
    assessment_filter_args = "assessment"
    model = models.Study
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, DjangoFilterBackend)
    list_actions = [
        "list",
        "rob_scores",
    ]

    def get_serializer_class(self):
        cls = serializers.VerboseStudySerializer
        if self.action == "list":
            cls = serializers.SimpleStudySerializer
        elif self.action == "create":
            cls = serializers.CreateStudySerializer
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
        assessment_id = tryParseInt(self.request.query_params.get("assessment_id"), -1)
        scores = self.model.objects.rob_scores(assessment_id)
        return Response(scores)

    @action(detail=False)
    def types(self, request):
        study_types = self.model.STUDY_TYPE_FIELDS
        return Response(study_types)

    def create(self, request):

        data = request.data.dict() if isinstance(request.data, QueryDict) else request.data
        reference_id = tryParseInt(data.pop("reference_id", -1), -1)

        try:
            reference = Reference.objects.get(id=reference_id)
        except ObjectDoesNotExist:
            raise ValidationError(f"Reference ID does not exist.")
        data["assessment"] = reference.assessment.id

        self.check_object_permissions(request, reference)

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=data, context={"reference_id": reference_id})
        serializer.is_valid(raise_exception=True)

        created_study = models.Study.save_new_from_reference(reference, serializer.validated_data)

        return Response(serializers.SimpleStudySerializer(created_study).data)


class FinalRobStudy(Study):
    list_actions = ["list"]

    def get_serializer_class(self):
        return serializers.FinalRobStudySerializer


class StudyCleanupFieldsView(CleanupFieldsBaseViewSet):
    model = models.Study
    serializer_class = serializers.StudyCleanupFieldsSerializer
