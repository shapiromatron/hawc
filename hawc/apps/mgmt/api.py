from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import BaseAssessmentViewSet
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.helper import FlatExport
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from . import exports, models
from .analytics import time_spent


class MgmtViewSet(BaseAssessmentViewSet):
    model = Assessment
    serializer_class = UnusedSerializer

    @action(
        detail=True,
        url_path="export",
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
        renderer_classes=PandasRenderers,
    )
    def tasks(self, request, pk):
        """
        Retrieve task export.
        """
        assessment: Assessment = self.get_object()
        qs = (
            models.Task.objects.get_qs(assessment)
            .select_related("study", "owner", "type", "status")
            .order_by("study_id", "type", "id")
        )
        exporter = exports.TaskExporter.flat_export(qs, filename=f"{assessment}-task")
        return Response(exporter)

    @action(
        detail=True,
        url_path="time-spent",
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
        renderer_classes=PandasRenderers,
    )
    def time_spent(self, request, pk):
        """Time spent export."""
        assessment: Assessment = self.get_object()
        export = FlatExport(df=time_spent.time_spent_df(pk), filename=f"{assessment}-time-spent")
        return Response(export)
