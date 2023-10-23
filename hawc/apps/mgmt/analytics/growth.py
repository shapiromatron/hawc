import math

import numpy as np
import pandas as pd
import plotly.express as px
from django.db.models import Count, Q

from hawc.apps.animal import constants
from hawc.apps.animal.models import Endpoint, EndpointGroup, Experiment
from hawc.apps.lit.models import Reference, Search
from hawc.apps.study.models import Study


# literature screening data
def get_search_count(assessment_id):
    return Search.objects.filter(assessment_id=assessment_id).count()


def get_search_types(assessment_id):
    return (
        Search.objects.filter(assessment_id=assessment_id)
        .values("search_type")
        .annotate(total=Count("search_type"))
        .order_by("search_type")
    )


def search_refs_df(assessment_id):
    qs = (
        Search.objects.filter(assessment_id=assessment_id)
        .annotate(num_refs=Count("references"))
        .values("created", "title", "num_refs")
    )
    df = pd.DataFrame(qs)
    return df


def update_xscale(min_value: float, max_value: float) -> dict:
    min_value = 1 if pd.isna(min_value) else min_value
    max_value = 1 if pd.isna(max_value) else max_value
    values = np.power(
        10.0, range(math.floor(math.log10(min_value)), math.ceil(math.log10(max_value)) + 1)
    )
    return dict(
        tickmode="array",
        tickvals=values,
        ticktext=[f"{value:,g}" for value in values],
    )


def refs_per_import_plot(assessent_id):
    df = search_refs_df(assessent_id)
    df2 = df.query("num_refs > 0")
    fig = px.box(
        data_frame=df2,
        x="num_refs",
        log_x=True,
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
    df = pd.DataFrame(qs, columns=["year", "nyear"])
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
        title=f"<sub>Total: {df.nyear.sum():,}   |   # Missing year: {n_null:,}</sub>",
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
    df = pd.DataFrame(qs, columns=["id", "ntags"])
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


# studies data
def study_classifications(assessment_id):
    published_totals = (
        Study.objects.filter(assessment_id=assessment_id)
        .values("published")
        .annotate(total=Count("published"))
        .order_by("published")
    )
    try:
        published_total = next(iter([x for x in published_totals if x["published"]]))["total"]
    except StopIteration:
        published_total = 0
    try:
        unpublished_total = next(iter([x for x in published_totals if not x["published"]]))["total"]
    except StopIteration:
        unpublished_total = 0
    return {
        "total": Study.objects.filter(assessment_id=assessment_id).count(),
        "animal": Study.objects.filter(assessment_id=assessment_id)
        .annotate(n_exp=Count("experiments"))
        .filter(n_exp__gt=0)
        .count(),
        "epi": Study.objects.filter(assessment_id=assessment_id)
        .annotate(n_sp=Count("study_populations"))
        .filter(n_sp__gt=0)
        .count(),
        "epiv2": Study.objects.filter(assessment_id=assessment_id)
        .annotate(n_des=Count("designs"))
        .filter(n_des__gt=0)
        .count(),
        "rob": Study.objects.filter(assessment_id=assessment_id)
        .annotate(n_rob=Count("riskofbiases"))
        .filter(n_rob__gt=0)
        .count(),
        "published": published_total,
        "unpublished": unpublished_total,
    }


# animal data
def animal_group_df(assessment_id):
    qs = Endpoint.objects.filter(assessment_id=assessment_id).values_list(
        "animal_group__experiment__study_id",
        "animal_group__experiment__id",
        "animal_group_id",
        "id",
    )
    df = pd.DataFrame(data=qs, columns=["study", "experiment", "animal_group", "endpoint"])
    return df


def animal_counts(assessment_id):
    df = animal_group_df(assessment_id)
    return {
        "studies": df.study.nunique(),
        "experiments": df.experiment.nunique(),
        "animal_groups": df.animal_group.nunique(),
        "endpoints": df.endpoint.nunique(),
    }


def endpoints_extracted(assessment_id):
    return (
        Endpoint.objects.filter(assessment_id=assessment_id)
        .annotate(ngroups=Count("groups"))
        .filter(data_extracted=True, ngroups__gt=0)
        .count()
    )


def endpoints_ehv(assessment_id):
    return (
        Endpoint.objects.filter(assessment_id=assessment_id)
        .filter(
            Q(name_term__isnull=False)
            | Q(system_term__isnull=False)
            | Q(organ_term__isnull=False)
            | Q(effect_term__isnull=False)
            | Q(effect_subtype_term__isnull=False)
        )
        .count()
    )


def n_dose_response_groups(assessment_id):
    return EndpointGroup.objects.filter(endpoint__assessment_id=assessment_id).count()


def experiment_type_df(assessment_id):
    types = (
        Experiment.objects.filter(study__assessment_id=assessment_id)
        .values_list("type")
        .annotate(total=Count("type"))
        .order_by("type")
    )
    data = []
    for type, n in list(types):
        data.append((constants.ExperimentType(type).label, n))
    df = pd.DataFrame(data=data, columns=["type", "count"]).sort_values("count")
    return df


def experiment_type_plot(assessment_id):
    df = experiment_type_df(assessment_id)
    fig = px.bar(
        data_frame=df,
        y="type",
        x="count",
        orientation="h",
        text_auto=True,
        height=500,
        labels={"type": "Experiment type", "count": "# Experiments"},
    )
    return fig


def get_context_data(id: int) -> dict:
    context = {}
    # literature screening
    context["n"] = get_search_count(id)
    context["search_types"] = get_search_types(id)
    context["total_n_refs"] = total_n_refs(id)
    context["refs_per_import_plot"] = refs_per_import_plot(id)
    context["refs_by_year_plot"] = refs_by_year_plot(id)
    context["ref_tags_breakdown"] = ref_tags_breakdown(id)
    context["refs_tags_plot"] = refs_tags_plot(id)
    # studies
    context["study_types"] = study_classifications(id)
    # animal group
    context["animal_counts"] = animal_counts(id)
    context["n_endpoints_extracted"] = endpoints_extracted(id)
    context["n_endpoints_ehv"] = endpoints_ehv(id)
    context["n_dose_res_groups"] = n_dose_response_groups(id)
    context["experiment_type_plot"] = experiment_type_plot(id)
    return context
