import pandas as pd
import plotly.express as px
from django.db.models import Value
from django.db.models.functions import Concat

from ...assessment.models import Assessment, TimeSpentEditing
from ...common.helper import df_move_column
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


def time_spent_summary_df(df: pd.DataFrame) -> pd.DataFrame:
    df2 = (
        df.groupby("model")["seconds"]
        .describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95])
        .merge(df.groupby("model")["seconds"].sum() / 60 / 60, left_index=True, right_index=True)
        .rename(
            columns={
                "count": "N",
                "mean": "Mean (seconds)",
                "std": "SD (seconds)",
                "min": "Minimum (seconds)",
                "5%": "5th (seconds)",
                "25%": "25th (seconds)",
                "50%": "50th (seconds)",
                "75%": "75th (seconds)",
                "95%": "95th (seconds)",
                "max": "Maximum (seconds)",
                "seconds": "Total (hours)",
            }
        )
        .fillna("-")
        .reset_index()
    )
    df2["N"] = df2["N"].astype(int)
    df2 = df_move_column(df2, "Total (hours)", "N")
    df2 = df_move_column(df2, "Mean (seconds)", "Total (hours)")
    df2 = df_move_column(df2, "SD (seconds)", "Mean (seconds)")
    return df2


def get_context_data(assessment: Assessment) -> dict:
    df = time_spent_df(assessment.id)
    return {
        "assessment": assessment,
        "assessment_pk": assessment.id,
        "time_spent_per_model_plot": time_spent_per_model_plot(df),
        "total_time_spent": total_time_spent(df),
        "time_spent_tbl": time_spent_summary_df(df).to_html(
            index=False,
            classes="table table-striped",
            bold_rows=False,
            float_format=lambda d: f"{d:0.2f}",
            border=0,
        ),
    }
