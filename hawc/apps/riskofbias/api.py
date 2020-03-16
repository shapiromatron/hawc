from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework_extensions.mixins import ListUpdateModelMixin

from ..assessment.api import (
    AssessmentEditViewset,
    AssessmentLevelPermissions,
    AssessmentViewset,
    DisabledPagination,
    InAssessmentFilter,
    RequiresAssessmentID,
)
from ..assessment.models import TimeSpentEditing, Assessment
from ..study.models import Study
from ..common.api import BulkIdFilter, APIAdapterMixin
from ..common.views import TeamMemberOrHigherMixin, AssessmentPermissionsMixin
from ..common.renderers import PandasRenderers
from ..mgmt.models import Task
from ..riskofbias import exports
from . import models, serializers


class RiskOfBiasAssessmentViewset(AssessmentPermissionsMixin, APIAdapterMixin, viewsets.GenericViewSet):
    parent_model = Assessment
    model = Study
    permission_classes = (AssessmentLevelPermissions,)

    def get_queryset(self):

        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment.id)

    @detail_route(methods=("get",), url_path="export", renderer_classes=PandasRenderers)
    def export(self, request, pk):
        self.create_legacy_attr(pk)
        rob_name = self.assessment.get_rob_name_display().lower()
        exporter = exports.RiskOfBiasFlat(
            self.get_queryset(),
            export_format="excel",
            filename=f'{self.assessment}-{rob_name.replace(" ", "-")}',
            sheet_name=rob_name,
        )
        excel_response = exporter.build_response()

        return Response(self.excel_to_df(excel_response.content))

    @detail_route(methods=("get",), url_path="full-export", renderer_classes=PandasRenderers)
    def full_export(self, request, pk):
        self.create_legacy_attr(pk)
        rob_name = self.assessment.get_rob_name_display().lower()
        exporter = exports.RiskOfBiasCompleteFlat(
            self.get_queryset(),
            export_format="excel",
            filename=f'{self.assessment}-{rob_name.replace(" ", "-")}-complete',
            sheet_name=rob_name,
        )
        excel_response = exporter.build_response()

        return Response(self.excel_to_df(excel_response.content))


class RiskOfBiasDomain(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = "assessment"
    model = models.RiskOfBiasDomain
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, filters.DjangoFilterBackend)
    serializer_class = serializers.AssessmentDomainSerializer

    def get_queryset(self):
        return self.model.objects.all().prefetch_related("metrics")


class RiskOfBias(viewsets.ModelViewSet):
    assessment_filter_args = "study__assessment"
    model = models.RiskOfBias
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, filters.DjangoFilterBackend)
    serializer_class = serializers.RiskOfBiasSerializer

    def get_queryset(self):
        return self.model.objects.all().prefetch_related("study", "author", "scores__metric__domain")

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

    @detail_route(methods=["get"])
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


class AssessmentScoreViewset(TeamMemberOrHigherMixin, ListUpdateModelMixin, AssessmentEditViewset):
    model = models.RiskOfBiasScore
    pagination_class = DisabledPagination
    assessment_filter_args = "metric__domain_assessment"
    filter_backends = (BulkIdFilter,)
    serializer_class = serializers.RiskOfBiasScoreSerializer

    def get_assessment(self, request, *args, **kwargs):
        assessment_id = request.GET.get("assessment_id", None)
        if assessment_id is None:
            raise RequiresAssessmentID

        return get_object_or_404(self.parent_model, pk=assessment_id)

    @list_route()
    def choices(self, request):
        assessment_id = self.get_assessment(request)
        rob_assessment = models.RiskOfBiasAssessment.objects.get(assessment_id=assessment_id)
        return Response(rob_assessment.get_rob_response_values())

    def get_queryset(self):
        return self.model.objects.all()

    def post_save_bulk(self, queryset, update_bulk_dict):
        ids = list(queryset.values_list("id", flat=True))
        queryset.model.delete_caches(ids)

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
