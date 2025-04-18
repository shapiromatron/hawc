from ..assessment.api import (
    AssessmentEditViewSet,
    EditPermissionsCheckMixin,
)
from . import models, serializers


class ExperimentViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["study"]
    assessment_filter_args = "study__assessment"
    model = models.Experiment
    serializer_class = serializers.ExperimentSerializer
    filterset_fields = ("study",)


class ChemicalViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["experiment"]
    assessment_filter_args = "experiment__study__assessment"
    model = models.Chemical
    serializer_class = serializers.ChemicalSerializer
    filterset_fields = ("experiment",)


class AnimalGroupViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["experiment"]
    assessment_filter_args = "experiment__study__assessment"
    model = models.AnimalGroup
    serializer_class = serializers.AnimalGroupSerializer
    filterset_fields = ("experiment",)


class TreatmentViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["experiment"]
    assessment_filter_args = "experiment__study__assessment"
    model = models.Treatment
    serializer_class = serializers.TreatmentSerializer
    filterset_fields = ("experiment",)


class DoseGroupViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["treatment"]
    assessment_filter_args = "treatment__experiment__study__assessment"
    model = models.DoseGroup
    serializer_class = serializers.DoseGroupSerializer
    filterset_fields = ("treatment",)


class EndpointViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["experiment"]
    assessment_filter_args = "experiment__study__assessment"
    model = models.Endpoint
    serializer_class = serializers.EndpointSerializer
    filterset_fields = ("experiment",)


class ObservationTimeViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["endpoint"]
    assessment_filter_args = "endpoint__experiment__study__assessment"
    model = models.ObservationTime
    serializer_class = serializers.ObservationTimeSerializer
    filterset_fields = ("endpoint",)


class DataExtractionViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["experiment"]
    assessment_filter_args = "experiment__study__assessment"
    model = models.DataExtraction
    serializer_class = serializers.DataExtractionSerializer
    filterset_fields = ("experiment",)


class DoseResponseGroupLevelDataViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["data_extraction"]
    assessment_filter_args = "data_extraction__experiment__study__assessment"
    model = models.DoseResponseGroupLevelData
    serializer_class = serializers.DoseResponseGroupLevelDataSerializer
    filterset_fields = ("data_extraction",)


class DoseResponseAnimalLevelDataViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["data_extraction"]
    assessment_filter_args = "data_extraction__experiment__study__assessment"
    model = models.DoseResponseAnimalLevelData
    serializer_class = serializers.DoseResponseAnimalLevelDataSerializer
    filterset_fields = ("data_extraction",)


class StudyLevelValueViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["study"]
    assessment_filter_args = "study__assessment"
    model = models.StudyLevelValue
    serializer_class = serializers.StudyLevelValueSerializer
    filterset_fields = ("study",)
