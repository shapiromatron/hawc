from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
from django.db.models import Count
from django.db.models.functions import Trunc
from reversion.models import Revision


def _get_df(Model, freq: str, field: str) -> pd.DataFrame:
    qs = (
        Model.objects.all()
        .filter(**{f"{field}__gt": datetime.today() - timedelta(days=365)})
        .annotate(date=Trunc(field, freq))
        .order_by("date")
        .values("date")
        .annotate(n=Count(field))
    )
    return pd.DataFrame(data=qs)


def daily_changes():
    df = _get_df(Revision, "day", "date_created")
    df["weekday"] = df.date.dt.day_name()
    df["weekofyear"] = df.date.dt.isocalendar().week
    df["year"] = df.date.dt.year
    df["yr-wk"] = df.year.astype(str) + "-" + df.weekofyear.astype(str)
    lines = px.line(
        df,
        x="date",
        y="n",
        title="changes per day",
        markers=True,
        hover_data=["weekday"],
        range_y=[0, df.n.quantile(0.99)],
    )
    lines_data = df.loc[:, "n"].describe().to_frame()

    boxplot = px.box(
        df,
        x="weekday",
        y="n",
        points="all",
        color="weekday",
        hover_data=["date"],
        title="changes per day of week",
        category_orders={
            "weekday": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        },
        range_y=[0, df.n.quantile(0.99)],
    )
    boxplot_data = df.pivot(columns="weekday", values="n").describe()
    df_punchcard = (
        df.pivot(columns="yr-wk", index="weekday", values="n")
        .fillna(0)
        .astype(int)
        .reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    )

    def punchcard():
        return df_punchcard.style.background_gradient(cmap="Greens", vmin=0, vmax=df.n.max())

    return {
        "lines": lines,
        "lines_data": lines_data,
        "boxplot": boxplot,
        "boxplot_data": boxplot_data,
        "punchcard": punchcard,
    }
