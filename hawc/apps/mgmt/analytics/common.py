import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def percentage(numerator, denominator) -> float:
    """Calculate a percentage; handles division by zero in denominator."""
    try:
        return numerator / float(denominator)
    except ZeroDivisionError:
        return 0


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


def empty_plot() -> go.Figure:
    fig = px.line()
    fig.update_layout(xaxis_title="", yaxis_title="")
    fig.add_annotation(
        text="No Data Available",
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=15),
    )
    return fig


pd_html_config = dict(
    index=False,
    classes="table table-striped",
    bold_rows=False,
    float_format=lambda d: f"{d:0.2f}",
    border=0,
)
