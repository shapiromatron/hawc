from __future__ import absolute_import

from assessment.api.views import AssessmentViewset

from . import models, serializers


class IVChemical(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVChemical
    serializer_class = serializers.IVChemicalSerializer


class IVExperiment(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVExperiment
    serializer_class = serializers.IVExperimentSerializer


class IVEndpoint(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVEndpoint
    serializer_class = serializers.IVEndpointSerializer
