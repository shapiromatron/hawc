from __future__ import absolute_import

import django_filters
from rest_framework import filters
from rest_framework import viewsets

from utils.api import DisabledPagination
from assessment.api.views import AssessmentLevelPermissions, InAssessmentFilter

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

    def get_serializer_class(self):
        cls = serializers.VerboseStudySerializer
        if self.action == "list":
            cls = serializers.SimpleStudySerializer
        return cls

    def get_queryset(self):
        prefetch = ()
        if self.action != "list":
            prefetch = (
                'qualities',
                'identifiers',
                'qualities__metric',
                'qualities__metric__domain'
            )

        return self.model.objects.all()\
                   .select_related('assessment')\
                   .prefetch_related(*prefetch)
