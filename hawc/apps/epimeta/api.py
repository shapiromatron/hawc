from rest_framework import viewsets, decorators
from rest_framework.response import Response

from ..assessment.api import AssessmentViewset, AssessmentLevelPermissions
from ..assessment.models import Assessment
from ..common.api import APIAdapterMixin
from ..common.renderers import PandasRenderers
from ..common.views import AssessmentPermissionsMixin
from . import models, serializers, exports


class EpiMetaAssessmentViewset(AssessmentPermissionsMixin, APIAdapterMixin, viewsets.GenericViewSet):
    parent_model = Assessment
    model = models.MetaResult
    permission_classes = (AssessmentLevelPermissions,)

    def get_queryset(self):
        perms = self.get_obj_perms()
        if not perms["edit"]:
            return self.model.objects.published(self.assessment)
        return self.model.objects.get_qs(self.assessment)

    @decorators.detail_route(methods=("get",), url_path="export", renderer_classes=PandasRenderers)
    def export(self, request, pk):
        """
        Retrieve epidemiology metadata for assessment.
        """
        self.create_legacy_attr(pk)
        exporter = exports.MetaResultFlatComplete(self.get_queryset(), export_format="excel",)
        excel_response = exporter.build_response()
        return Response(self.excel_to_df(excel_response.content))


class MetaProtocol(AssessmentViewset):
    assessment_filter_args = "study__assessment"
    model = models.MetaProtocol
    serializer_class = serializers.MetaProtocolSerializer


class MetaResult(AssessmentViewset):
    assessment_filter_args = "protocol__study__assessment"
    model = models.MetaResult
    serializer_class = serializers.MetaResultSerializer
