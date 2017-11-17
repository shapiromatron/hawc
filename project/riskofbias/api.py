

from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework import viewsets
from rest_framework_extensions.mixins import ListUpdateModelMixin

from assessment.api import AssessmentLevelPermissions, AssessmentEditViewset,\
    AssessmentViewset, DisabledPagination, InAssessmentFilter, RequiresAssessmentID
from utils.api import BulkIdFilter
from utils.views import TeamMemberOrHigherMixin

from assessment.models import TimeSpentEditing
from mgmt.models import Task
from . import models, serializers


class RiskOfBiasDomain(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = 'assessment'
    model = models.RiskOfBiasDomain
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, filters.DjangoFilterBackend)
    serializer_class = serializers.AssessmentDomainSerializer

    def get_queryset(self):
        return self.model.objects.all().prefetch_related('metrics')


class RiskOfBias(viewsets.ModelViewSet):
    assessment_filter_args = 'study__assessment'
    model = models.RiskOfBias
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, filters.DjangoFilterBackend)
    serializer_class = serializers.RiskOfBiasSerializer

    def get_queryset(self):
        return self.model.objects.all()\
            .prefetch_related('study', 'author', 'scores__metric__domain')

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
                serializer.instance.get_assessment().id
            )

class AssessmentMetricAnswersViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.RiskOfBiasMetricAnswers
    serializer_class = serializers.AssessmentMetricAnswersSerializer
    pagenation_class = DisabledPagination
    assessment_filter_args = "answers__metric_domain"

    def get_queryset(self):
        return self.model.objects.all()

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

class AssessmentMetricAnswersRecordedViewset(viewsets.ReadOnlyModelViewSet):
    model = models.RiskOfBiasMetric
    serializer_class = serializers.AssessmentRiskOfBiasAnswersRecordedSerializer
    pagination_class = DisabledPagination
    assessment_filter_args = "metric__domain"

    def get_queryset(self):
        return self.model.objects.all()


class AssessmentScoreViewset(TeamMemberOrHigherMixin, ListUpdateModelMixin, AssessmentEditViewset):
    model = models.RiskOfBiasScore
    serializer_class = serializers.AssessmentRiskOfBiasScoreSerializer
    pagination_class = DisabledPagination
    assessment_filter_args = 'metric__domain_assessment'
    filter_backends = (BulkIdFilter, )

    def get_assessment(self, request, *args, **kwargs):
        assessment_id = request.GET.get('assessment_id', None)
        if assessment_id is None:
            raise RequiresAssessmentID

        return get_object_or_404(self.parent_model, pk=assessment_id)

    @list_route()
    def choices(self, request):
        return Response(models.RiskOfBiasScore.RISK_OF_BIAS_SCORE_CHOICES)

    def get_queryset(self):
        return self.model.objects.all()

    def post_save_bulk(self, queryset, update_bulk_dict):
        ids = list(queryset.values_list('id', flat=True))
        queryset.model.delete_caches(ids)
