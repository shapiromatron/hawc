import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Count, Q

from ...animal import constants
from ...animal.models import Endpoint, EndpointGroup, Experiment
from ...lit import constants as lc
from ...lit.models import Reference, Search
from ...study.models import Study
from ...summary import constants as sc
from ...summary.models import DataPivot, SummaryTable, Visual
from .common import empty_plot, update_xscale


# literature screening data
def get_search_count(assessment_id):
    return (
        Search.objects.filter(assessment_id=assessment_id)
        .exclude(source=lc.ReferenceDatabase.MANUAL)
        .count()
    )


def get_search_source(assessment_id):
    qs = Search.objects.filter(assessment_id=assessment_id)
    return {
        "searches": qs.filter(search_type=lc.SearchType.SEARCH).count(),
        "imports": qs.filter(search_type=lc.SearchType.IMPORT)
        .exclude(source=lc.ReferenceDatabase.MANUAL)
        .count(),
        "pubmed_imports": qs.filter(
            search_type=lc.SearchType.IMPORT, source=lc.ReferenceDatabase.PUBMED
        ).count(),
        "hero_imports": qs.filter(
            search_type=lc.SearchType.IMPORT, source=lc.ReferenceDatabase.HERO
        ).count(),
        "ris_imports": qs.filter(
            search_type=lc.SearchType.IMPORT, source=lc.ReferenceDatabase.RIS
        ).count(),
    }


def search_refs_df(assessment_id):
    qs = (
        Search.objects.filter(assessment_id=assessment_id)
        .annotate(num_refs=Count("references"))
        .values("created", "title", "num_refs")
    )
    df = pd.DataFrame(qs)
    return df


def refs_per_import_plot(assessent_id) -> go.Figure:
    df = search_refs_df(assessent_id)
    df2 = df.query("num_refs > 0")
    if df2.empty:
        return empty_plot()
    fig = px.box(
        data_frame=df2,
        x="num_refs",
        log_x=True,
        points="all",
        hover_name="title",
        labels={"num_refs": "Number References"},
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


def refs_by_year_plot(assessment_id) -> go.Figure:
    df = refs_by_year_df(assessment_id)
    df2 = df.dropna()
    if df2.empty:
        return empty_plot()
    n_null = df.year.isna().count()
    fig = px.area(
        data_frame=df2,
        x="year",
        y="nyear",
        log_y=True,
        title=f"<sub>Total: {df.nyear.sum():,}   |   # Missing year: {n_null:,}</sub>",
        labels={"year": "Year", "nyear": "#"},
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
    if df2.empty:
        return empty_plot()
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


def barchart_count_plot(df: pd.DataFrame, **kw):
    return px.bar(data_frame=df, y="type", x="count", orientation="h", text_auto=True, **kw)


def experiment_type_plot(assessment_id):
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
    if df.empty:
        return empty_plot()
    return barchart_count_plot(df, labels={"type": "Experiment type", "count": "# Experiments"})


# summary data
def summary_counts(assessment_id):
    dp_count = DataPivot.objects.assessment_qs(assessment_id).count()

    # visual by type
    types = (
        Visual.objects.assessment_qs(assessment_id)
        .values_list("visual_type")
        .annotate(total=Count("visual_type"))
        .order_by("visual_type")
    )
    data = []
    if dp_count:
        data.append(("Data Pivot", dp_count))
    for type, n in list(types):
        data.append((sc.VisualType(type).label.title(), n))
    df = pd.DataFrame(data=data, columns=["type", "count"]).sort_values("count")
    visual_barchart = (
        empty_plot()
        if df["count"].sum() == 0
        else barchart_count_plot(df, labels={"type": "Visual type", "count": "# Visuals"})
    )

    # tables by type
    types = (
        SummaryTable.objects.assessment_qs(assessment_id)
        .values_list("table_type")
        .annotate(total=Count("table_type"))
        .order_by("table_type")
    )
    data = []
    for type, n in list(types):
        data.append((sc.TableType(type).label.title(), n))
    df = pd.DataFrame(data=data, columns=["type", "count"]).sort_values("count")
    table_barchart = (
        empty_plot()
        if df["count"].sum() == 0
        else barchart_count_plot(df, labels={"type": "Table type", "count": "# Tables"})
    )

    return {
        "visual": Visual.objects.assessment_qs(assessment_id).count(),
        "datapivot": dp_count,
        "table": SummaryTable.objects.assessment_qs(assessment_id).count(),
        "visual_barchart": visual_barchart,
        "table_barchart": table_barchart,
    }


def get_context_data(id: int) -> dict:
    return {
        # literature screening
        "n": get_search_count(id),
        "search_source": get_search_source(id),
        "total_n_refs": total_n_refs(id),
        "refs_per_import_plot": refs_per_import_plot(id),
        "refs_by_year_plot": refs_by_year_plot(id),
        "ref_tags_breakdown": ref_tags_breakdown(id),
        "refs_tags_plot": refs_tags_plot(id),
        # studies
        "study_types": study_classifications(id),
        # animal group
        "animal_counts": animal_counts(id),
        "n_endpoints_extracted": endpoints_extracted(id),
        "n_endpoints_ehv": endpoints_ehv(id),
        "n_dose_res_groups": n_dose_response_groups(id),
        "experiment_type_plot": experiment_type_plot(id),
        # summary
        "summary_count": summary_counts(id),
    }
