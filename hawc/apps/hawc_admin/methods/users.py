from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px

from ...myuser.models import HAWCUser


def user_active():
    qs = HAWCUser.objects.filter(is_active=True).values("id", "last_login")
    df = pd.DataFrame(qs).set_index("id").sort_values(by="last_login", ascending=False)
    df.loc[:, "last_login"] = df.last_login.dt.tz_localize(None)
    ntotal = df.shape[0]

    reference = datetime(2021, 12, 31)

    data = []
    for days in [1, 7, 30, 60, 90, 120, 150, 180, 365]:
        n = df.query(
            f"last_login <= '{reference.strftime('%Y-%m-%d')}' and last_login >= '{(reference - timedelta(days=days)).strftime('%Y-%m-%d')}'"
        ).size
        data.append((days, n))

    df2 = pd.DataFrame(data, columns=["days", "nusers"]).sort_values("days", ascending=False)
    df2.loc[:, "frac_total"] = df2.nusers / ntotal
    df2.loc[:, "days"] = df2.days.astype(str)
    df2.loc[:, "text"] = (
        df2.nusers.astype(str) + f"/{ntotal} (" + df2.frac_total.apply(lambda x: f"{x:.0%}") + ")"
    )
    df2.head(10)
    return px.bar(
        df2,
        x="nusers",
        y="days",
        text="text",
        title="# of users since last login",
        labels={"nusers": "# users", "days": "days since last login"},
    )


def user_growth():
    qs = HAWCUser.objects.filter(is_active=True).values("id", "email", "date_joined")
    df = pd.DataFrame(data=qs).set_index("id")
    df.loc[:, "domain"] = df.email.str.split("@", expand=True)[1]
    df.loc[:, "date_joined"] = df.date_joined.dt.tz_localize(None)
    df = df.drop(columns=["email"])

    df1 = (
        df.set_index("date_joined")
        .groupby(pd.Grouper(freq="M"))
        .count()["domain"]
        .reset_index()
        .rename(columns={"domain": "n"})
    )
    fig1 = px.bar(
        df1,
        x="date_joined",
        y="n",
        title="Users joined per month",
        text="n",
        labels={"date_joined": "Date joined", "n": "New users"},
    )

    df2 = df.domain.value_counts()[:20].to_frame().reset_index()
    fig2 = px.bar(
        df2, x="count", y="domain", title="Top 20 most frequently used domains", height=600
    )

    return fig1, fig2


def last_login():
    qs = HAWCUser.objects.filter(is_active=True).values("id", "email", "date_joined", "last_login")
    df = pd.DataFrame(qs).set_index("id")
    df.loc[:, "date_joined"] = df.date_joined.dt.tz_localize(None)
    df.loc[:, "last_login"] = df.last_login.dt.tz_localize(None)
    df.loc[:, "domain"] = df.email.str.split("@", expand=True)[1]
    df.loc[:, "days_since_joined"] = (datetime.today() - df.date_joined).dt.days
    df.loc[:, "days_since_login"] = (datetime.today() - df.last_login).dt.days
    df = df.drop(columns=["email"]).sort_index()

    fig1 = px.scatter(
        df,
        x="days_since_joined",
        y="days_since_login",
        title="Days since last login",
        hover_name="domain",
        hover_data=["date_joined", "last_login"],
        labels={
            "days_since_joined": "Days since joined",
            "days_since_login": "Days since last login",
        },
    )

    fig2 = px.histogram(
        df,
        x="days_since_login",
        marginal="rug",
        title="Number of days since last login",
        labels={"days_since_login": "Days"},
    )

    return fig1, fig2
