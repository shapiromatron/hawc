import logging
from typing import Any

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from ..assessment.api import (
    AssessmentEditViewSet,
    AssessmentViewSet,
    BaseAssessmentViewSet,
    CleanupFieldsBaseViewSet,
    CleanupFieldsPermissions,
    check_assessment_query_permission,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment, TimeSpentEditing
from ..common.api import DisabledPagination
from ..common.api.utils import get_published_only
from ..common.helper import tryParseInt
from ..common.renderers import PandasRenderers
from ..common.serializers import ExportQuerySerializer, UnusedSerializer
from ..common.validators import validate_exact_ids
from ..mgmt.models import Task
from ..riskofbias import exports
from ..study.models import Study
from . import models, serializers
from .actions.rob_clone import BulkRobCopyAction

logger = logging.getLogger(__name__)


class RiskOfBiasAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    @action(
        detail=True,
        url_path="export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export(self, request, pk):
        """
        Get all final risk of bias/study evaluations for an assessment.
        """
        self.get_object()
        ser = ExportQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        published_only = get_published_only(self.assessment, request)
        rob_name = self.assessment.get_rob_name_display().lower()
        qs = (
            models.RiskOfBiasScore.objects.filter(
                riskofbias__active=True,
                riskofbias__final=True,
                riskofbias__study__assessment=self.assessment,
            )
            .published_only(published_only)
            .order_by("riskofbias__study__short_citation", "riskofbias_id", "id")
        )
        filename = f"{self.assessment}-{rob_name}"
        exporter = exports.RiskOfBiasExporter.flat_export(qs, filename)
        return Response(exporter)

    @action(
        detail=True,
        url_path="full-export",
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
        renderer_classes=PandasRenderers,
    )
    def full_export(self, request, pk):
        """
        Get all risk of bias/study evaluations for an assessment, including individual reviews.
        """
        self.get_object()
        ser = ExportQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        published_only = get_published_only(self.assessment, request)
        rob_name = self.assessment.get_rob_name_display().lower()
        qs = (
            models.RiskOfBiasScore.objects.filter(
                riskofbias__active=True,
                riskofbias__study__assessment=self.assessment,
            )
            .published_only(published_only)
            .order_by("riskofbias__study__short_citation", "riskofbias_id", "id")
        )
        filename = f"{self.assessment}-{rob_name}-complete"
        exporter = exports.RiskOfBiasCompleteExporter.flat_export(qs, filename)
        return Response(exporter)

    @action(detail=False, methods=("post",), permission_classes=(IsAuthenticated,))
    def bulk_rob_copy(self, request):
        """
        Bulk copy risk of bias responses from one assessment to another.
        """
        return BulkRobCopyAction.handle_request(request, atomic=True)

    @action(
        detail=True, url_path="settings", action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT
    )
    def rob_settings(self, request, pk):
        self.get_object()
        ser = serializers.AssessmentRiskOfBiasSerializer(self.assessment)
        return Response(ser.data)


class RiskOfBiasDomain(AssessmentViewSet):
    assessment_filter_args = "assessment"
    model = models.RiskOfBiasDomain
    pagination_class = DisabledPagination
    serializer_class = serializers.NestedDomainSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related("metrics")

    @action(detail=False, methods=("patch",), permission_classes=(CleanupFieldsPermissions,))
    def order_rob(self, request):
        """Reorder domains/metrics in the order specified.

        The requests.data is expected to be a list in the following format:
            list[tuple[int, list[int]]] where, the first item in the tuple is a domain_id and
            the second is al ist of metric_ids associated with that domain.
        """
        qs = self.get_queryset().filter(assessment=self.assessment).prefetch_related("metrics")
        domain_id_to_domain = {domain.id: domain for domain in qs}
        metric_id_to_metric = {
            metric.id: metric for domain in qs for metric in domain.metrics.all()
        }
        domain_id_to_metric_ids = {
            domain.id: [metric.id for metric in domain.metrics.all()] for domain in qs
        }
        updated_domains = []
        updated_metrics = []

        expected_domain_ids = list(domain_id_to_metric_ids.keys())
        domain_ids = [domain_id for domain_id, _ in request.data]
        validate_exact_ids(expected_domain_ids, domain_ids, "domain")
        for i, (domain_id, metric_ids) in enumerate(request.data, start=1):
            expected_metric_ids = domain_id_to_metric_ids[domain_id]
            validate_exact_ids(expected_metric_ids, metric_ids, "metric")

            domain = domain_id_to_domain[domain_id]
            if domain.sort_order != i:
                domain.sort_order = i
                updated_domains.append(domain)

            for j, metric_id in enumerate(metric_ids, start=1):
                metric = metric_id_to_metric[metric_id]
                if metric.sort_order != j:
                    metric.sort_order = j
                    updated_metrics.append(metric)

        if updated_domains:
            obj_ids = [obj.id for obj in updated_domains]
            logger.info(f"Updating order for assessment {self.assessment.id}, domains {obj_ids}")
            models.RiskOfBiasDomain.objects.bulk_update(updated_domains, ["sort_order"])

        if updated_metrics:
            obj_ids = [obj.id for obj in updated_metrics]
            logger.info(f"Updating order for assessment {self.assessment.id}, metrics {obj_ids}")
            models.RiskOfBiasMetric.objects.bulk_update(updated_metrics, ["sort_order"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class RiskOfBias(AssessmentEditViewSet):
    assessment_filter_args = "study__assessment"
    model = models.RiskOfBias
    pagination_class = DisabledPagination
    serializer_class = serializers.RiskOfBiasSerializer
    action_perms = {
        "retrieve": AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
        "list": AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
    }
    filterset_fields = ("study",)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("study", "author")
            .prefetch_related("scores__overridden_objects")
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
                self.request,
                serializer.instance,
                serializer.instance.get_assessment().id,
                url=serializer.instance.get_edit_url(),
            )

    def create(self, request, *args, **kwargs):
        study_id = tryParseInt(request.data.get("study_id"), -1)

        try:
            study = Study.objects.get(id=study_id)
        except ObjectDoesNotExist as err:
            raise ValidationError("Invalid study_id") from err

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

    @action(detail=True, methods=["get"], action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT)
    def override_options(self, request, pk=None):
        object_ = self.get_object()
        return Response(object_.get_override_options())

    @action(detail=False, url_path="assignment", methods=("post",), permission_classes=[])
    def create_assignment(self, request):
        # perms checked in serializer
        kw = {"context": self.get_serializer_context()}
        serializer = serializers.RiskOfBiasAssignmentSerializer(data=request.data, **kw)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, url_path="assignment", methods=("patch",), permission_classes=[])
    def update_assignment(self, request, *args, **kwargs):
        # perms checked in serializer
        instance = self.get_object()
        kw = {"context": self.get_serializer_context()}
        serializer = serializers.RiskOfBiasAssignmentSerializer(
            instance, data=request.data, partial=True, **kw
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, url_path="final")
    def final(self, request):
        """
        Get all active, final evaluations for an assessment.

        To get a single review final review for a study, use the study detail API
        """
        # check permissions
        assessment = check_assessment_query_permission(
            request, AssessmentViewSetPermissions.CAN_VIEW_OBJECT
        )
        # query data
        filters: dict[str, Any] = dict(study__assessment=assessment, final=True, active=True)
        if study := tryParseInt(request.query_params.get("study")):
            filters["study"] = study
        if not assessment.user_is_team_member_or_higher(self.request.user):
            filters["study__published"] = True
        robs = models.RiskOfBias.objects.filter(**filters).prefetch_related(
            "scores__overridden_objects"
        )
        serializer = serializers.FinalRiskOfBiasSerializer(robs, many=True)
        return Response(serializer.data)


class AssessmentMetricViewSet(AssessmentViewSet):
    model = models.RiskOfBiasMetric
    serializer_class = serializers.RiskOfBiasMetricSerializer
    pagination_class = DisabledPagination
    assessment_filter_args = "domain__assessment"

    @action(detail=True, action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER)
    def scores(self, request, *args, **kwargs):
        metric = self.get_object()
        serializer = serializers.MetricFinalScoresSerializer(metric)
        return Response(serializer.data)


class AssessmentScoreViewSet(AssessmentEditViewSet):
    model = models.RiskOfBiasScore
    pagination_class = DisabledPagination
    assessment_filter_args = "metric__domain__assessment"
    serializer_class = serializers.RiskOfBiasScoreSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related("overridden_objects__content_object")

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
        super().perform_destroy(instance)


class ScoreCleanupViewSet(CleanupFieldsBaseViewSet):
    model = models.RiskOfBiasScore
    serializer_class = serializers.RiskOfBiasScoreCleanupSerializer
    assessment_filter_args = "metric__domain__assessment"
