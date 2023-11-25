import pandas as pd
import plotly.express as px
from django.db.models import Value
from django.db.models.functions import Concat

from hawc.apps.assessment.models import TimeSpentEditing

from .growth import update_xscale


def time_spent_df(assessment_id: int) -> pd.DataFrame:
    qs = TimeSpentEditing.objects.filter(seconds__gt=0, assessment_id=assessment_id).values_list(
        "id",
        "seconds",
        "content_type__app_label",
        Concat("content_type__app_label", Value("."), "content_type__model"),
    )
    df = pd.DataFrame(data=qs, columns="id|seconds|app|model".split("|")).sort_values(
        ["app", "model"]
    )
    return df


def time_spent_per_model_plot(df: pd.DataFrame):
    fig = px.box(
        data_frame=df,
        y="model",
        x="seconds",
        log_x=True,
        points="outliers",
        height=600,
    )
    fig.layout["xaxis"].update(**update_xscale(df.seconds.min(), df.seconds.max()))
    return fig


def total_time_spent(df: pd.DataFrame) -> str:
    hr = df.seconds.sum() / 60 / 60
    if hr < 40:
        return f"{hr:,.1f} hours"
    elif hr < 200:
        return f"{hr/8:,.1f} work days"
    else:
        return f"{hr/8/5:,.1f} work weeks"


def time_tbl(df: pd.DataFrame) -> str:
    return (
        (df.groupby("model").seconds.sum() / 3600)
        .reset_index()
        .rename(columns={"seconds": "hours"})
        .sort_values("hours", ascending=False)
        .to_html(
            index=False,
            classes="table table-striped",
            bold_rows=False,
            float_format=lambda d: f"{d:0.2f}",
            border=0,
        )
    )


def get_context_data(id: int) -> dict:
    df = time_spent_df(id)
    return {
        "time_spent_per_model_plot": time_spent_per_model_plot(df),
        "total_time_spent": total_time_spent(df),
        "time_spent_tbl": time_tbl(df),
    }
