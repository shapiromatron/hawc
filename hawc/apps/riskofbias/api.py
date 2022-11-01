import logging

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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
from ..common.api import (
    CleanupFieldsBaseViewSet,
    CleanupFieldsPermissions,
    LegacyAssessmentAdapterMixin,
)
from ..common.helper import re_digits, tryParseInt
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..common.validators import validate_exact_ids
from ..common.views import AssessmentPermissionsMixin
from ..mgmt.models import Task
from ..riskofbias import exports
from ..study.models import Study
from . import models, serializers
from .actions.rob_clone import BulkRobCopyAction

logger = logging.getLogger(__name__)


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

    @action(detail=True, url_path="export", renderer_classes=PandasRenderers)
    def export(self, request, pk):
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        rob_name = self.assessment.get_rob_name_display().lower()
        exporter = exports.RiskOfBiasFlat(
            self.get_queryset().none(),
            filename=f"{self.assessment}-{rob_name}",
            assessment_id=self.assessment.id,
        )

        return Response(exporter.build_export())

    @action(detail=True, url_path="full-export", renderer_classes=PandasRenderers)
    def full_export(self, request, pk):
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        rob_name = self.assessment.get_rob_name_display().lower()
        exporter = exports.RiskOfBiasCompleteFlat(
            self.get_queryset().none(),
            filename=f"{self.assessment}-{rob_name}-complete",
            assessment_id=self.assessment.id,
        )
        return Response(exporter.build_export())

    @action(detail=False, methods=("post",), permission_classes=(IsAuthenticated,))
    def bulk_rob_copy(self, request):
        """
        Bulk copy risk of bias responses from one assessment to another.
        """
        return BulkRobCopyAction.handle_request(request, atomic=True)

    @action(detail=True, url_path="settings")
    def rob_settings(self, request, pk):
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        ser = serializers.AssessmentRiskOfBiasSerializer(self.assessment)
        return Response(ser.data)


class RiskOfBiasDomain(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = "assessment"
    model = models.RiskOfBiasDomain
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, DjangoFilterBackend)
    serializer_class = serializers.NestedDomainSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        return self.model.objects.all().prefetch_related("metrics")

    @action(detail=False, methods=("patch",), permission_classes=(CleanupFieldsPermissions,))
    def order_rob(self, request):
        """Reorder domains/metrics in the order specified.

        The requests.data is expected to be a list in the following format:
            List[Tuple[int, List[int]]] where, the first item in the tuple is a domain_id and
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


class RiskOfBias(AssessmentEditViewset):
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

    @action(detail=False, methods=("post",))
    def create_v2(self, request):
        kw = {"context": self.get_serializer_context()}
        serializer = serializers.RiskOfBiasAssignmentSerializer(data=request.data, **kw)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=("patch",))
    def update_v2(self, request, *args, **kwargs):
        instance = self.get_object()
        kw = {"context": self.get_serializer_context()}
        serializer = serializers.RiskOfBiasAssignmentSerializer(
            instance, data=request.data, partial=True, **kw
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class AssessmentMetricViewset(AssessmentViewset):
    model = models.RiskOfBiasMetric
    serializer_class = serializers.RiskOfBiasMetricSerializer
    pagination_class = DisabledPagination
    assessment_filter_args = "domain__assessment"

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentMetricScoreViewset(AssessmentViewset):
    model = models.RiskOfBiasMetric
    serializer_class = serializers.MetricFinalScoresSerializer
    pagination_class = DisabledPagination
    assessment_filter_args = "domain__assessment"

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentScoreViewset(AssessmentEditViewset):
    model = models.RiskOfBiasScore
    pagination_class = DisabledPagination
    assessment_filter_args = "metric__domain__assessment"
    serializer_class = serializers.RiskOfBiasScoreSerializer
    list_actions = ["list", "v2"]

    def get_assessment(self, request, *args, **kwargs):
        assessment_id = get_assessment_id_param(request)
        return get_object_or_404(self.parent_model, pk=assessment_id)

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


class ScoreCleanupViewset(CleanupFieldsBaseViewSet):
    model = models.RiskOfBiasScore
    serializer_class = serializers.RiskOfBiasScoreCleanupSerializer
    assessment_filter_args = "metric__domain__assessment"
