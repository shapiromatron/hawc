from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentLevelPermissions,
    AssessmentRootedTagTreeViewset,
    AssessmentViewset,
    CleanupFieldsBaseViewSet,
)
from ..assessment.models import Assessment
from ..common.constants import AssessmentViewSetPermissions
from ..common.helper import re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from . import exports, models, serializers


class IVAssessmentViewset(viewsets.GenericViewSet):
    model = Assessment
    queryset = Assessment.objects.all()
    permission_classes = (AssessmentLevelPermissions,)
    action_perms = {}
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

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


class IVChemical(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVChemical
    serializer_class = serializers.IVChemicalSerializer


class IVCellType(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVCellType
    serializer_class = serializers.IVCellTypeSerializer


class IVExperiment(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.IVExperiment
    serializer_class = serializers.IVExperimentSerializerFull


class IVEndpointCategory(AssessmentRootedTagTreeViewset):
    model = models.IVEndpointCategory
    serializer_class = serializers.IVEndpointCategorySerializer


class IVEndpoint(AssessmentViewset):
    assessment_filter_args = "assessment"
    model = models.IVEndpoint
    serializer_class = serializers.IVEndpointSerializer


class IVEndpointCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.IVEndpointCleanupFieldsSerializer
    model = models.IVEndpoint
    assessment_filter_args = "assessment"


class IVChemicalCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.IVChemicalCleanupFieldsSerializer
    model = models.IVChemical
    assessment_filter_args = "study__assessment"
