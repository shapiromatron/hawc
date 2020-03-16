from rest_framework import decorators, viewsets
from rest_framework.response import Response
from ..assessment.api import AssessmentRootedTagTreeViewset, AssessmentViewset, AssessmentLevelPermissions
from ..assessment.models import Assessment
from ..common.api import CleanupFieldsBaseViewSet, APIAdapterMixin
from ..common.renderers import PandasRenderers
from ..common.views import AssessmentPermissionsMixin
from . import exports, models, serializers


class IVAssessmentViewset(AssessmentPermissionsMixin, APIAdapterMixin, viewsets.GenericViewSet):
    parent_model = Assessment
    model = models.IVEndpoint
    permission_classes = (AssessmentLevelPermissions,)

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment)

    @decorators.detail_route(methods=("get",), url_path="full-export", renderer_classes=PandasRenderers)
    def full_export(self, request, pk):
        self.create_legacy_attr(pk)
        self.object_list = self.get_queryset()
        export_format = request.GET.get("output", "excel")
        exporter = exports.DataPivotEndpoint(
            self.object_list, export_format=export_format, filename=f"{self.assessment}-invitro",
        )
        excel_response = exporter.build_response()
        return Response(self.excel_to_df(excel_response.content))


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


class IVChemicalCleanup(CleanupFieldsBaseViewSet):
    serializer_class = serializers.IVChemicalCleanupFieldsSerializer
    model = models.IVChemical
    assessment_filter_args = "study__assessment"
