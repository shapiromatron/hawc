import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Count
from django.db.models.functions import Trunc

from ...lit.models import Reference
from ...riskofbias.models import RiskOfBias
from ...study.models import Study
from ...summary.models import DataPivot, Visual
from .common import empty_plot


def get_data(
    Model, freq: str, assessment_id: int, filter_str: str = "assessment_id"
) -> pd.DataFrame:
    qs = (
        Model.objects.all()
        .filter(**{filter_str: assessment_id})
        .annotate(date=Trunc("created", freq))
        .order_by("date")
        .values("date")
        .annotate(n=Count("created"))
    )
    return pd.DataFrame(data=qs, columns=["date", "n"])


def time_series(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_plot()
    df2 = df.set_index("date").cumsum().reset_index()
    fig = px.line(df2, x="date", y="n")
    return fig


def get_context_data(id: int) -> dict:
    viz_per_year = get_data(Visual, "month", id)
    dp_per_year = get_data(DataPivot, "month", id)
    return {
        "refs": time_series(get_data(Reference, "month", id)),
        "studies": time_series(get_data(Study, "month", id)),
        "robs": time_series(get_data(RiskOfBias, "month", id, "study__assessment_id")),
        "visuals": time_series(viz_per_year),
        "datapivots": time_series(dp_per_year),
        "total_visuals": time_series(
            pd.concat([viz_per_year, dp_per_year]).groupby("date").sum().reset_index()
        ),
    }
