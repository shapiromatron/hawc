from __future__ import absolute_import

from assessment.api.views import AssessmentViewset

from . import models, serializers


class StudyPopulation(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.StudyPopulation
    serializer_class = serializers.StudyPopulationSerializer


class Outcome(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Outcome
    serializer_class = serializers.OutcomeSerializer


class GroupCollection(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.GroupCollection
    serializer_class = serializers.GroupCollectionSerializer


class Group(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.Group
    serializer_class = serializers.GroupSerializer
