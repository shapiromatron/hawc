from __future__ import absolute_import

from assessment.api import AssessmentViewset

from . import models, serializers
from utils.api import CleanupFieldsBaseViewSet


class IVChemical(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVChemical
    serializer_class = serializers.IVChemicalSerializer


class IVCellType(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVCellType
    serializer_class = serializers.IVCellTypeSerializer


class IVExperiment(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVExperiment
    serializer_class = serializers.IVExperimentSerializerFull


class IVEndpoint(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVEndpoint
    serializer_class = serializers.IVEndpointSerializer


class IVEndpointCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.IVEndpointCleanupFieldsSerializer
    model = models.IVEndpoint


class IVChemicalCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.IVChemicalCleanupFieldsSerializer
    model = models.IVChemical
    assessment_filter_args = "study__assessment"

