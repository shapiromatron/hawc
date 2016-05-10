from __future__ import absolute_import

import django_filters
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from assessment.api.views import (
    AssessmentLevelPermissions, InAssessmentFilter, DisabledPagination)

from . import models, serializers


class StudyFilters(django_filters.FilterSet):
    study_type = django_filters.ChoiceFilter(
        choices=models.Study.STUDY_TYPE_CHOICES)

    class Meta:
        model = models.Study
        fields = ('study_type', )


class Study(viewsets.ReadOnlyModelViewSet):
    assessment_filter_args = "assessment"
    model = models.Study
    pagination_class = DisabledPagination
    permission_classes = (AssessmentLevelPermissions, )
    filter_backends = (InAssessmentFilter, filters.DjangoFilterBackend)
    filter_class = StudyFilters
    list_actions = ['list', 'rob_scores', ]

    def get_serializer_class(self):
        cls = serializers.VerboseStudySerializer
        if self.action == "list":
            cls = serializers.SimpleStudySerializer
        return cls

    def get_queryset(self):
        filters = {}
        prefetch = ()

        if self.action == "list":
            if not self.assessment.user_can_edit_object(self.request.user):
                filters["published"] = True
        else:
            prefetch = (
                'riskofbiases__scores',
                'identifiers',
                'riskofbiases__scores__metric',
                'riskofbiases__scores__metric__domain',
            )

        return self.model.objects.filter(**filters)\
                   .prefetch_related(*prefetch)

    @list_route()
    def rob_scores(self, request):
        assessment_id = int(self.request.query_params.get('assessment_id', -1))
        scores = models.Study.rob_scores(assessment_id)
        return Response(scores)
