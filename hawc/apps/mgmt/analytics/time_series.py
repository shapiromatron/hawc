import pandas as pd
import plotly.express as px
from django.db.models import Count
from django.db.models.functions import Trunc

from hawc.apps.lit.models import Reference
from hawc.apps.summary.models import DataPivot, Visual


def get_data(Model, freq):
    qs = (
        Model.objects.all()
        .annotate(date=Trunc("created", freq))
        .order_by("date")
        .values("date")
        .annotate(n=Count("created"))
    )
    df = pd.DataFrame(data=qs)
    return df


def time_series(Model, df):
    fig = px.line(df, x="date", y="n", title=Model.__name__)
    return fig


def get_time_series_data(self, **kwargs):
    context = {}
    context["visuals_per_year"] = time_series(Visual, get_data(Visual, "year"))
    context["datapivots_per_year"] = time_series(DataPivot, get_data(DataPivot, "year"))
    context["total_visuals"] = time_series(
        Visual,
        pd.concat([get_data(Visual, "year"), get_data(DataPivot, "year")])
        .groupby("date")
        .sum()
        .reset_index(),
    )
    context["refs_per_month"] = time_series(Reference, get_data(Reference, "month"))
    return context
