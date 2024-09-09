from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentRootedTagTreeViewSet,
    AssessmentViewSet,
    BaseAssessmentViewSet,
    CleanupFieldsBaseViewSet,
)
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.api.utils import get_published_only
from ..common.renderers import PandasRenderers
from ..common.serializers import ExportQuerySerializer, UnusedSerializer
from . import exports, models, serializers


class IVAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    def get_endpoint_queryset(self, request):
        published_only = get_published_only(self.assessment, request)
        if published_only:
            return models.IVEndpoint.objects.published(self.assessment).order_by("id")
        return models.IVEndpoint.objects.get_qs(self.assessment).order_by("id")

    @action(
        detail=True,
        url_path="full-export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def full_export(self, request, pk):
        """
        Retrieve complete in vitro data

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.get_object()
        ser = ExportQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        self.object_list = self.get_endpoint_queryset(request)
        exporter = exports.DataPivotEndpoint(
            self.object_list, filename=f"{self.assessment}-invitro", assessment=self.assessment
        )
        return Response(exporter.build_export())


class IVChemical(AssessmentViewSet):
    assessment_filter_args = "study__assessment"
    model = models.IVChemical
    serializer_class = serializers.IVChemicalSerializer


class IVCellType(AssessmentViewSet):
    assessment_filter_args = "study__assessment"
    model = models.IVCellType
    serializer_class = serializers.IVCellTypeSerializer


class IVExperiment(AssessmentViewSet):
    assessment_filter_args = "study__assessment"
    model = models.IVExperiment
    serializer_class = serializers.IVExperimentSerializerFull


class IVEndpointCategory(AssessmentRootedTagTreeViewSet):
    model = models.IVEndpointCategory
    serializer_class = serializers.IVEndpointCategorySerializer


class IVEndpoint(AssessmentViewSet):
    assessment_filter_args = "assessment"
    model = models.IVEndpoint
    serializer_class = serializers.IVEndpointSerializer


class IVEndpointCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.IVEndpointCleanupFieldsSerializer
    model = models.IVEndpoint
    assessment_filter_args = "assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("experiment__study")


class IVChemicalCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.IVChemicalCleanupFieldsSerializer
    model = models.IVChemical
    assessment_filter_args = "study__assessment"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().select_related("study")
