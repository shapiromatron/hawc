import math

import numpy as np
import pandas as pd
import plotly.express as px
from django.db.models import Count

from hawc.apps.lit.models import Reference, Search


def get_search_count(assessment_id):
    return Search.objects.filter(assessment_id=assessment_id).count()


def get_search_types(assessment_id):
    return (
        Search.objects.filter(assessment_id=assessment_id)
        .values("search_type")
        .annotate(total=Count("search_type"))
        .order_by("search_type")
    )


def refs_df(assessment_id):
    qs = (
        Search.objects.filter(assessment_id=assessment_id)
        .annotate(num_refs=Count("references"))
        .values("created", "title", "num_refs")
    )
    df = pd.DataFrame(qs)
    return df


def update_xscale(min_value: float, max_value: float) -> dict:
    values = np.power(
        10.0, range(math.floor(math.log10(min_value)), math.ceil(math.log10(max_value)) + 1)
    )
    return dict(
        tickmode="array",
        tickvals=values,
        ticktext=[f"{value:,g}" for value in values],
    )


def refs_per_import_plot(assessent_id):
    df = refs_df(assessent_id)
    df2 = df.query("num_refs > 0")
    fig = px.box(
        data_frame=df2,
        x="num_refs",
        log_x=True,
        title="Num references per import",
        points="all",
        hover_name="title",
    )
    fig.layout["xaxis"].update(**update_xscale(df2.num_refs.min(), df2.num_refs.max()))
    return fig


def total_n_refs(assessment_id):
    return Reference.objects.filter(assessment_id=assessment_id).count()


def refs_by_year_df(assessment_id):
    qs = (
        Reference.objects.filter(assessment_id=assessment_id)
        .values("year")
        .annotate(nyear=Count("year"))
        .order_by("year")
    )
    df = pd.DataFrame(qs)
    return df


def refs_by_year_plot(assessment_id):
    df = refs_by_year_df(assessment_id)
    df2 = df.dropna()
    n_null = df.year.isna().count()
    fig = px.area(
        data_frame=df2,
        x="year",
        y="nyear",
        log_y=True,
        title=f"Reference per year<br><sub>Total: {df.nyear.sum():,}   |   # Missing year: {n_null:,}</sub>",
    )
    fig.layout["yaxis"].update(**update_xscale(df2.nyear.min(), df2.nyear.max()))
    return fig


def n_tags_per_ref(assessment_id):
    qs = (
        Reference.objects.filter(assessment_id=assessment_id)
        .values("id")
        .annotate(ntags=Count("tags"))
        .order_by("ntags")
    )
    df = pd.DataFrame(qs)
    return df


def ntags_nrefs_df(assessment_id):
    df = n_tags_per_ref(assessment_id)
    df2 = df.groupby("ntags").count().rename(columns={"id": "num_refs"}).reset_index()
    return df2


def ref_tags_breakdown(assessment_id):
    df2 = ntags_nrefs_df(assessment_id)
    no_tags = (
        Reference.objects.filter(assessment_id=assessment_id)
        .annotate(ntags=Count("tags"))
        .filter(ntags=0)
        .count()
    )
    with_tags = (
        Reference.objects.filter(assessment_id=assessment_id)
        .annotate(ntags=Count("tags"))
        .filter(ntags__gt=0)
        .count()
    )
    total_tags_applied = (df2.ntags * df2.num_refs).sum()
    return dict(no_tags=no_tags, with_tags=with_tags, total_tags_applied=total_tags_applied)


def refs_tags_plot(assessment_id):
    df2 = ntags_nrefs_df(assessment_id)
    fig = px.bar(
        data_frame=df2,
        y="ntags",
        x="num_refs",
        log_x=True,
        orientation="h",
        text_auto=True,
        height=500,
        labels={"num_refs": "Number of References", "ntags": "# Tags applied"},
    )
    fig.layout["xaxis"].update(**update_xscale(df2.num_refs.min(), df2.num_refs.max()))
    return fig


def get_context_data(self, **kwargs):
    id = self.assessment.id
    context = dict()
    context["n"] = get_search_count(id)
    context["search_types"] = get_search_types(id)
    context["total_n_refs"] = total_n_refs(id)
    context["refs_per_import_plot"] = refs_per_import_plot(id)
    context["refs_by_year_plot"] = refs_by_year_plot(id)
    context["ref_tags_breakdown"] = ref_tags_breakdown(id)
    context["refs_tags_plot"] = refs_tags_plot(id)
    return context
