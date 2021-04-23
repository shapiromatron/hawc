from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from ..assessment.api import (
    AssessmentEditViewset,
    AssessmentLevelPermissions,
    AssessmentViewset,
    DisabledPagination,
    InAssessmentFilter,
    get_assessment_id_param,
)
from ..assessment.models import Assessment, TimeSpentEditing
from ..common.api import CleanupFieldsBaseViewSet, LegacyAssessmentAdapterMixin
from ..common.helper import re_digits, tryParseInt
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from ..mgmt.models import Task
from ..riskofbias import exports
from ..study.models import Study
from . import models, serializers
from .actions.rob_clone import BulkRobCopyAction


class RiskOfBiasAssessmentViewset(
    AssessmentPermissionsMixin, LegacyAssessmentAdapterMixin, viewsets.GenericViewSet
):
    parent_model = Assessment
    model = Study
    permission_classes = (AssessmentLevelPermissions,)
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):

        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment.id)

    @action(detail=True, methods=("get",), url_path="export", renderer_classes=PandasRenderers)
    def export(self, request, pk):
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        rob_name = self.assessment.get_rob_name_display().lower()
        exporter = exports.RiskOfBiasFlat(
            self.get_queryset(), filename=f"{self.assessment}-{rob_name}"
        )

        return Response(exporter.build_export())

    @action(detail=True, methods=("get",), url_path="full-export", renderer_classes=PandasRenderers)
    def full_export(self, request, pk):
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        rob_name = self.assessment.get_rob_name_display().lower()
        exporter = exports.RiskOfBiasCompleteFlat(
            self.get_queryset(), filename=f"{self.assessment}-{rob_name}-complete"
        )
        return Response(exporter.build_export())

    @action(detail=False, methods=("post",), permission_classes=(IsAdminUser,))
    def bulk_rob_copy(self, request):
        """
        Bulk copy risk of bias responses from one assessment to another.
        """
        return BulkRobCopyAction.handle_request(request, atomic=True)


class RiskOfBiasDomain(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = "assessment"
    model = models.RiskOfBiasDomain
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, DjangoFilterBackend)
    serializer_class = serializers.AssessmentDomainSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all().prefetch_related("metrics")


class RiskOfBias(viewsets.ModelViewSet):
    assessment_filter_args = "study__assessment"
    model = models.RiskOfBias
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, DjangoFilterBackend)
    serializer_class = serializers.RiskOfBiasSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all().prefetch_related(
            "study", "author", "scores__metric__domain"
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        study = serializer.instance.study
        user = self.request.user
        Task.objects.ensure_rob_started(study, user)
        if serializer.instance.final and serializer.instance.is_complete:
            Task.objects.ensure_rob_stopped(study)

        # send time complete task
        if not serializer.errors:
            TimeSpentEditing.add_time_spent_job(
                self.request.session.session_key,
                serializer.instance.get_edit_url(),
                serializer.instance,
                serializer.instance.get_assessment().id,
            )

    def create(self, request, *args, **kwargs):
        study_id = tryParseInt(request.data.get("study_id"), -1)

        try:
            study = Study.objects.get(id=study_id)
        except ObjectDoesNotExist:
            raise ValidationError("Invalid study_id")

        # permission check using the user submitting the request
        if not study.user_can_edit_study(study.assessment, request.user):
            raise PermissionDenied(
                f"Submitter '{request.user}' has invalid permissions to edit Risk of Bias for this study"
            )

        # overridden_objects is not marked as optional in RiskOfBiasScoreSerializerSlim; if it's not present
        # in the payload, let's just add an empty array.
        scores = request.data.get("scores")
        for score in scores:
            if "overridden_objects" not in score:
                score["overridden_objects"] = []

        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=["get"])
    def override_options(self, request, pk=None):
        object_ = self.get_object()
        return Response(object_.get_override_options())


class AssessmentMetricViewset(AssessmentViewset):
    model = models.RiskOfBiasMetric
    serializer_class = serializers.AssessmentMetricChoiceSerializer
    pagination_class = DisabledPagination
    assessment_filter_args = "domain__assessment"

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentMetricScoreViewset(AssessmentViewset):
    model = models.RiskOfBiasMetric
    serializer_class = serializers.AssessmentMetricScoreSerializer
    pagination_class = DisabledPagination
    assessment_filter_args = "domain__assessment"

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentScoreViewset(AssessmentEditViewset):
    model = models.RiskOfBiasScore
    pagination_class = DisabledPagination
    assessment_filter_args = "metric__domain__assessment"
    serializer_class = serializers.RiskOfBiasScoreSerializer

    def get_assessment(self, request, *args, **kwargs):
        assessment_id = get_assessment_id_param(request)
        return get_object_or_404(self.parent_model, pk=assessment_id)

    @action(detail=False)
    def choices(self, request):
        assessment_id = self.get_assessment(request)
        rob_assessment = models.RiskOfBiasAssessment.objects.get(assessment_id=assessment_id)
        return Response(rob_assessment.get_rob_response_values())

    def create(self, request, *args, **kwargs):
        # create using one serializer; return using a different one
        serializer = serializers.RiskOfBiasScoreOverrideCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        new_serializer = serializers.RiskOfBiasScoreSerializer(serializer.instance)
        headers = self.get_success_headers(new_serializer.data)
        return Response(new_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_destroy(self, instance):
        if instance.is_default:
            raise PermissionDenied("Cannot delete a default risk of bias score")
        instance.delete()


class ScoreCleanupViewset(CleanupFieldsBaseViewSet):
    model = models.RiskOfBiasScore
    serializer_class = serializers.RiskOfBiasScoreCleanupSerializer
    assessment_filter_args = "metric__domain__assessment"
