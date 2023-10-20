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
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from . import exports, models, serializers


class IVAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    def get_endpoint_queryset(self):
        perms = self.assessment.user_permissions(self.request.user)
        if not perms["edit"]:
            return models.IVEndpoint.objects.published(self.assessment).order_by("id")
        return models.IVEndpoint.objects.get_qs(self.assessment).order_by("id")

    @action(
        detail=True,
        url_path="full-export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def full_export(self, request, pk):
        self.get_object()
        self.object_list = self.get_endpoint_queryset()
        exporter = exports.DataPivotEndpoint(
            self.object_list, filename=f"{self.assessment}-invitro"
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
