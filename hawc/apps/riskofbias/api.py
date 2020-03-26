from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework_extensions.mixins import ListUpdateModelMixin

from ..assessment.api import (
    AssessmentEditViewset,
    AssessmentLevelPermissions,
    AssessmentViewset,
    DisabledPagination,
    InAssessmentFilter,
    RequiresAssessmentID,
)
from ..assessment.models import TimeSpentEditing
from ..common.api import BulkIdFilter
from ..common.helper import tryParseInt
from ..common.views import TeamMemberOrHigherMixin
from ..mgmt.models import Task
from ..study.models import Study
from . import models, serializers


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
        requester_has_appropriate_permissions = False
        study_id = tryParseInt(request.data.get("study_id"), -1)
        study = Study.objects.get(id=study_id)
        if study.user_can_edit_study(study.assessment, request.user):
            # request.user is the user represented by the "Authorization: Token xxxx" header.
            requester_has_appropriate_permissions = True

        if not requester_has_appropriate_permissions:
            raise ValidationError("Submitter '%s' has invalid permissions to edit Risk of Bias for this study" % request.user)

        # overridden_objects is not marked as optional in RiskOfBiasScoreSerializerSlim; if it's not present
        # in the payload, let's just add an empty array.
        scores = request.data.get("scores")
        for score in scores:
            if "overridden_objects" not in score:
                score["overridden_objects"] = []

        return super().create(request, args, kwargs)

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
