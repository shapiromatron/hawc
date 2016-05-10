from __future__ import absolute_import

from rest_framework import filters
from rest_framework import viewsets

from assessment.api.views import AssessmentLevelPermissions, InAssessmentFilter, DisabledPagination

from . import models, serializers


class RiskOfBiasDomain(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = 'assessment'
    model = models.RiskOfBiasDomain
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions,)
    filter_backends = (InAssessmentFilter, filters.DjangoFilterBackend)
    serializer_class = serializers.AssessmentDomainSerializer

    def get_queryset(self):
        return self.model.objects.all()
