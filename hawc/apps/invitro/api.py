from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import (
    AssessmentLevelPermissions,
    AssessmentRootedTagTreeViewset,
    AssessmentViewset,
)
from ..assessment.models import Assessment
from ..common.api import CleanupFieldsBaseViewSet, LegacyAssessmentAdapterMixin
from ..common.helper import re_digits
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..common.views import AssessmentPermissionsMixin
from . import actions, models, serializers


class IVAssessmentViewset(
    AssessmentPermissionsMixin, LegacyAssessmentAdapterMixin, viewsets.GenericViewSet
):
    parent_model = Assessment
    model = models.IVEndpoint
    permission_classes = (AssessmentLevelPermissions,)
    serializer_class = UnusedSerializer
    lookup_value_regex = re_digits

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment).order_by("id")
        return self.model.objects.get_qs(self.assessment).order_by("id")

    @action(detail=True, methods=("get",), url_path="full-export", renderer_classes=PandasRenderers)
    def full_export(self, request, pk):
        self.set_legacy_attr(pk)
        self.permission_check_user_can_view()
        self.object_list = self.get_queryset()
        filename = f"{self.assessment}-invitro"
        exporter = actions.DataPivotEndpoint(self.object_list, filename=filename)
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
