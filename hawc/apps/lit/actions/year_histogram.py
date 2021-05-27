from typing import Optional

import pandas as pd
import plotly.express as px
from plotly.graph_objs._figure import Figure

from ..models import Reference


def reference_year_histogram(assessment) -> Optional[Figure]:
    """
    Return plotly express histogram for years in an assessment if data exists, otherwise
    return nothing.
    """
    # get all the years for a given assessment
    years = list(
        Reference.objects.filter(assessment=assessment, year__gt=0).values_list("year", flat=True)
    )
    if len(years) == 0:
        return None

    df = pd.DataFrame(years, columns=["Year"])
    nbins = min(max(df.Year.max() - df.Year.min() + 1, 4), 30)

    try:
        fig = px.histogram(df, x="Year", nbins=nbins)
    except ValueError:
        # in some cases a bad nbins can be provided; just use default bins instead
        # Invalid value of type 'numpy.int64' received for the 'nbinsx' property of histogram
        # [2005, 2013, 1995, 2001, 2017, 1991, 1991, 2009, 2006, 2005]; nbins=27
        fig = px.histogram(df, x="Year")

    fig.update_yaxes(title_text="# References")
    fig.update_xaxes(title_text="Year")
    fig.update_traces(marker=dict(color="#003d7b"))

    fig.update_layout(
        bargap=0.1,
        plot_bgcolor="white",
        autosize=True,
        margin=dict(l=0, r=0, t=30, b=0),  # noqa: E741
    )
    return fig
