from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import AssessmentViewSet, BaseAssessmentViewSet
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.api.utils import get_published_only
from ..common.renderers import PandasRenderers
from ..common.serializers import ExportQuerySerializer, UnusedSerializer
from . import exports, models, serializers


class EpiMetaAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    def get_meta_result_queryset(self, request):
        published_only = get_published_only(self.assessment, request)
        if published_only:
            return models.MetaResult.objects.published(self.assessment)
        return models.MetaResult.objects.get_qs(self.assessment)

    @action(
        detail=True,
        url_path="export",
        action_perms=AssessmentViewSetPermissions.CAN_VIEW_OBJECT,
        renderer_classes=PandasRenderers,
    )
    def export(self, request, pk):
        """
        Retrieve epidemiology meta-analysis data for an assessment.

        By default only shows data from published studies. If the query param `unpublished=true`
        is present then results from all studies are shown.
        """
        self.get_object()
        ser = ExportQuerySerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)
        exporter = exports.MetaResultFlatComplete(
            self.get_meta_result_queryset(request), filename=f"{self.assessment}-epi-meta"
        )
        return Response(exporter.build_export())


class MetaProtocol(AssessmentViewSet):
    assessment_filter_args = "study__assessment"
    model = models.MetaProtocol
    serializer_class = serializers.MetaProtocolSerializer


class MetaResult(AssessmentViewSet):
    assessment_filter_args = "protocol__study__assessment"
    model = models.MetaResult
    serializer_class = serializers.MetaResultSerializer
