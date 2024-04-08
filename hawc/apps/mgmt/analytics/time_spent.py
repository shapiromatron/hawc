import pandas as pd
import plotly.express as px
from django.db.models import Value
from django.db.models.functions import Concat

from ...assessment.models import Assessment, TimeSpentEditing
from .common import update_xscale


def time_spent_df(assessment_id: int) -> pd.DataFrame:
    qs = TimeSpentEditing.objects.filter(seconds__gt=0, assessment_id=assessment_id).values_list(
        "content_type__app_label",
        Concat("content_type__app_label", Value("."), "content_type__model"),
        "id",
        "seconds",
    )
    df = pd.DataFrame(data=qs, columns="app|model|id|seconds".split("|")).sort_values(
        ["app", "model", "id"]
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


def time_tbl(df: pd.DataFrame) -> pd.DataFrame:
    return (
        (df.groupby("model").seconds.sum() / 3600)
        .reset_index()
        .rename(columns={"seconds": "hours"})
        .sort_values("hours", ascending=False)
    )


def standard_deviation_tbl(df: pd.DataFrame) -> pd.DataFrame:
    df["hours"] = df["seconds"] / 3600
    percentiles = df.groupby("model")["hours"].quantile([0.05, 0.95, 0.25, 0.75]).unstack()
    percentiles.columns = ["5", "95", "25", "75"]
    for col in percentiles.columns:
        percentiles[col] = percentiles[col].round(2)
    return percentiles


def time_tbl_with_sd(df: pd.DataFrame) -> pd.DataFrame:
    hours_df = time_tbl(df)
    sd_df = standard_deviation_tbl(df)
    merged = pd.merge(hours_df, sd_df, on="model", how="left")
    merged["SD 5/95"] = merged.apply(lambda row: f"{row["5"]} / {row["95"]}", axis=1)
    merged["SD 25/75"] = merged.apply(lambda row: f"{row["25"]} / {row["75"]}", axis=1)
    merged = merged.drop(columns=["5", "95", "25", "75"])
    return merged


def get_context_data(assessment: Assessment) -> dict:
    df = time_spent_df(assessment.id)
    return {
        "assessment": assessment,
        "assessment_pk": assessment.id,
        "time_spent_per_model_plot": time_spent_per_model_plot(df),
        "total_time_spent": total_time_spent(df),
        "time_spent_tbl": time_tbl_with_sd(df).to_html(
            index=False,
            classes="table table-striped",
            bold_rows=False,
            float_format=lambda d: f"{d:0.2f}",
            border=0,
        ),
    }
