from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentEditViewSet,
    BaseAssessmentViewSet,
    CleanupFieldsBaseViewSet,
    EditPermissionsCheckMixin,
    InAssessmentFilter,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.api.utils import get_published_only
from ..common.helper import FlatExport
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..study.models import Study
from . import exports, models, serializers
from .actions.model_metadata import EpiV2Metadata


class EpiAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    @action(
        detail=True,
        url_path="export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export(self, request, pk):
        """
        Retrieve epidemiology complete export.
        """
        assessment: Assessment = self.get_object()
        published_only = get_published_only(assessment, request)
        qs = (
            models.DataExtraction.objects.get_qs(assessment)
            .published_only(published_only)
            .complete()
        )
        exporter = exports.EpiFlatComplete(qs, filename=f"{assessment}-epi")
        return Response(exporter.build_export())

    @action(
        detail=True,
        url_path="study-export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def study_export(self, request, pk):
        """
        Retrieve epidemiology at the study level for assessment.
        """
        assessment: Assessment = self.get_object()
        published_only = get_published_only(assessment, request)
        qs = (
            Study.objects.assessment_qs(assessment.id)
            .filter(epi=True)
            .published_only(published_only)
        )

        df = models.Design.objects.study_df(qs)
        return FlatExport.api_response(df=df, filename=f"epi-study-{assessment.id}")


class DesignViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["study"]
    assessment_filter_args = "study__assessment"
    model = models.Design
    serializer_class = serializers.DesignSerializer
    filter_backends = (InAssessmentFilter, DjangoFilterBackend)
    filterset_fields = ("study",)

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset()


class MetadataViewSet(viewsets.ViewSet):
    def list(self, request):
        return EpiV2Metadata.handle_request(request)


class ChemicalViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["design"]
    assessment_filter_args = "design__study__assessment"
    model = models.Chemical
    serializer_class = serializers.ChemicalSerializer


class ExposureViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["design"]
    assessment_filter_args = "design__study__assessment"
    model = models.Exposure
    serializer_class = serializers.ExposureSerializer


class ExposureLevelViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["design"]
    assessment_filter_args = "design__study__assessment"
    model = models.ExposureLevel
    serializer_class = serializers.ExposureLevelSerializer


class OutcomeViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["design"]
    assessment_filter_args = "design__study__assessment"
    model = models.Outcome
    serializer_class = serializers.OutcomeSerializer


class AdjustmentFactorViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["design"]
    assessment_filter_args = "design__study__assessment"
    model = models.AdjustmentFactor
    serializer_class = serializers.AdjustmentFactorSerializer


class DataExtractionViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["design"]
    assessment_filter_args = "design__study__assessment"
    model = models.DataExtraction
    serializer_class = serializers.DataExtractionSerializer

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all().select_related(
            "outcome", "exposure_level__exposure_measurement", "exposure_level__chemical", "factors"
        )


# Cleanup ViewSets
class DesignCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.DesignCleanupSerializer
    model = models.Design
    assessment_filter_args = "study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("study")


class ChemicalCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ChemicalCleanupSerializer
    model = models.Chemical
    assessment_filter_args = "design__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("design__study")


class ExposureCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ExposureCleanupSerializer
    model = models.Exposure
    assessment_filter_args = "design__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("design__study")


class ExposureLevelCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.ExposureLevelCleanupSerializer
    model = models.ExposureLevel
    assessment_filter_args = "design__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("design__study")


class OutcomeCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.OutcomeCleanupSerializer
    model = models.Outcome
    assessment_filter_args = "design__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("design__study")


class AdjustmentFactorCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.AdjustmentFactorCleanupSerializer
    model = models.AdjustmentFactor
    assessment_filter_args = "design__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("design__study")


class DataExtractionCleanupViewSet(CleanupFieldsBaseViewSet):
    serializer_class = serializers.DataExtractionCleanupSerializer
    model = models.DataExtraction
    assessment_filter_args = "design__study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("design__study")
