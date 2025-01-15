from typing import NamedTuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Count
from django.db.models.functions import Trunc

from ...animal.models import Endpoint, Experiment
from ...assessment.models import Assessment
from ...epi.models import Outcome, StudyPopulation
from ...epiv2 import models as epiv2models
from ...lit.models import Reference
from ...riskofbias.models import RiskOfBias
from ...study.models import Study
from ...summary.models import DataPivot, Visual
from .common import empty_plot, pd_html_config


class TimeSeries(NamedTuple):
    key: str
    figure: go.Figure
    table_html: str


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


def build_time_df(df: pd.DataFrame) -> pd.DataFrame | None:
    if df.empty:
        return None
    df2 = df.set_index("date").cumsum().reset_index().rename(columns={"n": "# items"})
    df2["Month"] = df2.date.dt.strftime("%B %Y")
    return df2[["Month", "# items"]]


def build_time_series(key: str, df: pd.DataFrame) -> TimeSeries:
    table = build_time_df(df)
    return TimeSeries(
        key=key,
        figure=time_series(df),
        table_html=table.to_html(**pd_html_config) if isinstance(table, pd.DataFrame) else "",
    )


def get_context_data(assessment: Assessment) -> dict:
    id = assessment.id
    viz_per_year = get_data(Visual, "month", id)
    dp_per_year = get_data(DataPivot, "month", id)
    context = {
        "assessment": assessment,
        "assessment_pk": id,
        "refs": build_time_series("ref", get_data(Reference, "month", id)),
        "studies": build_time_series("study", get_data(Study, "month", id)),
        "robs": build_time_series(
            "robs", get_data(RiskOfBias, "month", id, "study__assessment_id")
        ),
        "rob_title": f"{assessment.get_rob_name_display()} created over time",
        "experiments": build_time_series(
            "experiments", get_data(Experiment, "month", id, "study__assessment_id")
        ),
        "endpoints": build_time_series("endpoints", get_data(Endpoint, "month", id)),
        "visuals": build_time_series("visuals", viz_per_year),
        "datapivots": build_time_series("datapivots", dp_per_year),
        "total_visuals": build_time_series(
            "allviz", pd.concat([viz_per_year, dp_per_year]).groupby("date").sum().reset_index()
        ),
    }
    if assessment.epi_version == 1:
        context.update(
            sp=build_time_series(
                "sp", get_data(StudyPopulation, "month", id, "study__assessment_id")
            ),
            outcome=build_time_series("outcomes", get_data(Outcome, "month", id)),
        )
    elif assessment.epi_version == 2:
        context.update(
            sp=build_time_series(
                "sp", get_data(epiv2models.Design, "month", id, "study__assessment_id")
            ),
            outcome=build_time_series(
                "outcomes",
                get_data(epiv2models.Outcome, "month", id, "design__study__assessment_id"),
            ),
        )

    return context
