import pandas as pd
import plotly.express as px
from django.db.models import Count
from django.db.models.functions import Trunc

from hawc.apps.lit.models import Reference
from hawc.apps.summary.models import DataPivot, Visual


def get_data(Model, freq, assessment_id):
    qs = (
        Model.objects.all()
        .filter(assessment_id=assessment_id)
        .annotate(date=Trunc("created", freq))
        .order_by("date")
        .values("date")
        .annotate(n=Count("created"))
    )
    df = pd.DataFrame(data=qs, columns=["date", "n"])
    return df


def time_series(Model, df):
    if df.empty:
        fig = px.line()
        fig.update_layout(xaxis_title="date", yaxis_title="n")
        fig.add_annotation(
            text="No Data for this Assessment",
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=15),
        )
    else:
        fig = px.line(df, x="date", y="n", title=Model.__name__)
    return fig


def get_context_data(id: int) -> dict:
    context = {}
    context["visuals_per_year"] = time_series(Visual, get_data(Visual, "year", id))
    context["datapivots_per_year"] = time_series(DataPivot, get_data(DataPivot, "year", id))
    context["total_visuals"] = time_series(
        Visual,
        pd.concat([get_data(Visual, "year", id), get_data(DataPivot, "year", id)])
        .groupby("date")
        .sum()
        .reset_index(),
    )
    context["refs_per_month"] = time_series(Reference, get_data(Reference, "month", id))
    return context
