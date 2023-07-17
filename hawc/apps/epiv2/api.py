from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentEditViewSet,
    BaseAssessmentViewSet,
    CleanupFieldsBaseViewSet,
    EditPermissionsCheckMixin,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.renderers import PandasRenderers
from . import exports, models, serializers
from .actions.model_metadata import EpiV2Metadata


class EpiAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment

    @action(
        detail=True,
        url_path="export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export(self, request, pk):
        """
        Retrieve epidemiology data for assessment.
        """
        assessment: Assessment = self.get_object()
        published_only = not assessment.user_can_edit_object(request.user)
        qs = (
            models.DataExtraction.objects.get_qs(assessment)
            .published_only(published_only)
            .complete()
        )
        exporter = exports.EpiFlatComplete(qs, filename=f"{assessment}-epi")
        return Response(exporter.build_export())


class DesignViewSet(EditPermissionsCheckMixin, AssessmentEditViewSet):
    edit_check_keys = ["study"]
    assessment_filter_args = "study__assessment"
    model = models.Design
    serializer_class = serializers.DesignSerializer

    def get_queryset(self, *args, **kwargs):
        return self.model.objects.all()


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
