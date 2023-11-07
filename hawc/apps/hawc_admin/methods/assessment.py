from datetime import timedelta

import pandas as pd
import plotly.express as px
from django import forms
from django.db.models import Count, F
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ...animal.models import Endpoint
from ...assessment.models import Assessment
from ...common.helper import HAWCtoDateString
from ...lit.models import Reference
from ...riskofbias.models import RiskOfBias
from ...study.models import Study
from ...summary.models import DataPivot, Visual
from .constants import PandasDurationGrouper


def _get_data(Model, order_by="assessment_id"):
    qs = (
        Model.objects.all()
        .filter(created__gt=timezone.now() - timedelta(days=180))
        .order_by(order_by)
        .values(assess_id=F(order_by))
        .annotate(n=Count("id"))
        .order_by("-n")
    )
    df = pd.DataFrame(data=qs)
    df.loc[:, "field"] = Model.__name__
    return df


def growth_matrix():
    df = pd.concat(
        [
            _get_data(Reference),
            _get_data(Study),
            _get_data(RiskOfBias, "study__assessment_id"),
            _get_data(Endpoint),
            _get_data(Visual),
            _get_data(DataPivot),
        ]
    )

    df2 = pd.DataFrame(Assessment.objects.filter(id__in=df.assess_id.unique()).values("id", "name"))
    df2 = df.merge(df2, left_on="assess_id", right_on="id").drop(columns=["id"])
    df2.loc[:, "assessment"] = df2.name + " [" + df2.assess_id.astype(str) + "]"
    df2 = df2.drop(columns=["assess_id", "name"])

    df3 = df2.pivot(index="assessment", columns="field").fillna(0).astype(int).droplevel(0, axis=1)
    df3 = df3[["Reference", "Study", "RiskOfBias", "Endpoint", "Visual", "DataPivot"]]

    # relative effort for each item in a count; a visual is 10x harder to create than a study
    # a study is 20x harder to select than a reference
    weights = pd.Series([0.05, 1, 2, 3, 10, 10], index=df3.columns.tolist())
    order = df3.dot(weights).sort_values(ascending=False).index
    return df3.reindex(order)[:20].style.background_gradient(cmap="PuBu")


class AssessmentGrowthSettings(forms.Form):
    assessment_id = forms.IntegerField(label="Assessment")
    grouper = forms.ChoiceField(
        choices=PandasDurationGrouper.choices,
        initial=PandasDurationGrouper.weekly,
        label="Grouping frequency",
        required=False,
    )
    log = forms.BooleanField(label="Logscale", initial=True, required=False)

    def time_series(self):
        data = self.cleaned_data
        assessment_id = data["assessment_id"] or self.fields["assessment_id"].initial
        grouper = data["grouper"] or self.fields["grouper"].initial
        log_y = data["log"] if data and "log" in data else self.fields["log"].initial

        assessment = get_object_or_404(Assessment, id=assessment_id)

        start = assessment.created
        Models = [
            (Reference, "assessment_id"),
            (Study, "assessment_id"),
            (RiskOfBias, "study__assessment_id"),
            (Endpoint, "assessment_id"),
            (Visual, "assessment_id"),
            (DataPivot, "assessment_id"),
        ]

        dfs = []
        for Model, filter_str in Models:
            qs = Model.objects.filter(**{filter_str: assessment.id}).values("id", "created")
            df = pd.DataFrame(qs)
            if df.shape[0] > 0:
                df = (
                    df.rename(columns={"created": "date"})
                    .set_index("date")
                    .groupby(pd.Grouper(freq=grouper))
                    .count()
                    .cumsum()
                    .reset_index()
                )
                df.loc[:, "model"] = Model.__name__
                dfs.append(df)

        if len(dfs) == 0:
            raise Http404()

        df = pd.concat(dfs)
        end = df.date.max() + timedelta(days=14)
        df = pd.concat(
            [
                pd.Series(df.model.unique(), name="model").to_frame().assign(date=start, id=0),
                df,
                df.groupby("model")
                .max()["id"]
                .to_frame()
                .assign(date=timezone.now())
                .reset_index(),
            ]
        ).sort_values(["model", "date"], ascending=True)

        fig = px.line(
            df,
            x="date",
            y="id",
            color="model",
            log_y=log_y,
            range_x=[start, end],
            title=f"{assessment}: item creation timeline",
            labels={"id": "# items", "date": "created date"},
        )
        return assessment, fig


def size_df() -> pd.DataFrame:
    """Get the item count for many key item types in an assessment dataframe"""
    qs = Assessment.objects.all().values("id", "name", "created", "last_updated")
    df1 = pd.DataFrame(qs).set_index("id")
    for annotation in [
        dict(num_references=Count("references")),
        dict(num_studies=Count("references__study")),
        dict(num_ani_endpoints=Count("baseendpoint__endpoint")),
        dict(num_epi_outcomes=Count("baseendpoint__outcome")),
        dict(num_epi_results=Count("baseendpoint__outcome__results")),
        dict(num_invitro_ivendpoints=Count("baseendpoint__ivendpoint")),
        dict(num_datapivots=Count("datapivot")),
        dict(num_viusals=Count("visuals")),
    ]:
        qs = Assessment.objects.all().values("id").annotate(**annotation)
        df2 = pd.DataFrame(qs).set_index("id")
        df1 = df1.merge(df2, left_index=True, right_index=True)

    df1 = df1.reset_index().sort_values("id")

    # stringify datetimes
    df1[["created", "last_updated"]] = df1[["created", "last_updated"]].map(HAWCtoDateString)

    # apply hyperlink to assessment names
    df1["name"] = df1[["id", "name"]].apply(
        lambda row: f"<a href='/assessment/{row['id']}/'>{row['name']}</a>", axis=1
    )

    # format column names for readability
    return df1.rename(lambda c: c.replace("_", " "), axis="columns")
