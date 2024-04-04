import pandas as pd
from rest_framework import exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..assessment.api import BaseAssessmentViewSet
from ..assessment.constants import AssessmentViewSetPermissions
from ..assessment.models import Assessment
from ..common.helper import FlatExport
from ..common.renderers import PandasRenderers
from ..common.serializers import UnusedSerializer
from ..lit.models import Reference
from ..riskofbias.models import RiskOfBias
from ..study.models import Study
from ..summary.models import DataPivot, Visual
from . import exports, models
from .analytics import time_series, time_spent


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
            .select_related("study", "owner")
            .order_by("study_id", "type", "id")
        )
        exporter = exports.TaskExporter.flat_export(qs, filename=f"{assessment}-task")
        return Response(exporter)

    @action(
        detail=True,
        url_path="time-spent",
        action_perms=AssessmentViewSetPermissions.PROJECT_MANAGER_OR_HIGHER,
        renderer_classes=PandasRenderers,
    )
    def time_spent(self, request, pk):
        """Time spent export."""
        assessment: Assessment = self.get_object()
        df = time_spent.time_spent_df(pk)
        time_table = time_spent.time_tbl_with_sd(df)
        export = FlatExport(df=time_table, filename=f"{assessment}-time-spent")
        return Response(export)

    @action(
        detail=True,
        url_path=r"time-series/(?P<type>[\w]+)",
        action_perms=AssessmentViewSetPermissions.TEAM_MEMBER_OR_HIGHER,
        renderer_classes=PandasRenderers,
    )
    def time_series(self, request, pk, type: str):
        """References over time series export."""

        time_series_data = {
            "reference": (Reference, "month", pk),
            "study": (Study, "month", pk),
            "rob": (RiskOfBias, "month", pk, "study__assessment_id"),
            "visual": (Visual, "month", pk),
            "data_pivot": (DataPivot, "month", pk),
            "total_visuals": None,
        }

        if type not in time_series_data:
            raise exceptions.ValidationError({"detail": "Invalid type"})

        args = time_series_data[type]
        if args is None:
            df = (
                pd.concat(
                    [
                        time_series.get_data(*time_series_data["visual"]),
                        time_series.get_data(*time_series_data["data_pivot"]),
                    ]
                )
                .groupby("date")
                .sum()
                .reset_index()
            )
        else:
            df = time_series.get_data(*args)

        assessment: Assessment = self.get_object()
        df["date"] = df["date"].dt.strftime("%m/%d/%Y")
        df = df.set_index("date").cumsum().reset_index()
        export = FlatExport(df=df, filename=f"{assessment}-{type}-time-series")
        return Response(export)
