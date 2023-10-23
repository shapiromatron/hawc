import pandas as pd
import plotly.express as px
from django.db.models import Value
from django.db.models.functions import Concat

from hawc.apps.assessment.models import TimeSpentEditing

from .growth import update_xscale


def time_spent_df(assessment_id):
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


def time_spent_per_model_plot(assessment_id):
    df = time_spent_df(assessment_id)
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


def total_time_spent(assessment_id):
    df = time_spent_df(assessment_id)
    return f"{df.seconds.sum()/60/60:,.1f} hours"


def get_context_data(id: int) -> dict:
    context = {}
    context["time_spent_per_model_plot"] = time_spent_per_model_plot(id)
    context["total_time_spent"] = total_time_spent(id)
    return context
