from __future__ import absolute_import
from rest_framework.response import Response

from assessment.api.views import AssessmentViewset

from . import models, serializers


class StudyPopulation(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.StudyPopulation
    serializer_class = serializers.StudyPopulationSerializer


class Exposure(AssessmentViewset):
    assessment_filter_args = "study_population__study__assessment"
    model = models.Exposure
    serializer_class = serializers.ExposureSerializer


class Outcome(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Outcome
    serializer_class = serializers.OutcomeSerializer


class Result(AssessmentViewset):
    assessment_filter_args = "outcome__assessment"
    model = models.Result
    serializer_class = serializers.ResultSerializer


class ComparisonSet(AssessmentViewset):
    assessment_filter_args = "assessment"  # todo: fix
    model = models.ComparisonSet
    serializer_class = serializers.ComparisonSetSerializer


class Group(AssessmentViewset):
    assessment_filter_args = "assessment"  # todo: fix
    model = models.Group
    serializer_class = serializers.GroupSerializer

class CleanupFields(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Outcome
    serializer_class = serializers.CleanupSerializer

    def list(self, request, format=None):
        cleanup_fields = self.model.text_cleanup_fields()
        return Response({'text_cleanup_fields': cleanup_fields})
