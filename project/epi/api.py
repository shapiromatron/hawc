from __future__ import absolute_import

from assessment.api.views import AssessmentViewset

from . import models, serializers


class MetaResult(AssessmentViewset):
    assessment_filter_args = "protocol__study__assessment"
    model = models.MetaResult
    serializer_class = serializers.MetaResultSerializer


class StudyPopulation(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.StudyPopulation
    serializer_class = serializers.StudyPopulationSerializer


class Exposure(AssessmentViewset):
    assessment_filter_args = "study_population__study__assessment"
    model = models.Exposure
    serializer_class = serializers.ExposureVerboseSerializer


class AssessedOutcome(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.AssessedOutcome
    serializer_class = serializers.AssessedOutcomeSerializer
