from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import AssessmentViewSet, BaseAssessmentViewSet
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from . import exports, models, serializers


class EpiMetaAssessmentViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    def get_meta_result_queryset(self):
        perms = self.assessment.user_permissions(self.request.user)
        if not perms["edit"]:
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
        """
        self.get_object()
        exporter = exports.MetaResultFlatComplete(
            self.get_meta_result_queryset(), filename=f"{self.assessment}-epi-meta"
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
