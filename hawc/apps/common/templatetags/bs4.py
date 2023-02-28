"""
Twitter Bootstrap 4 - helper methods
"""
from textwrap import dedent
from typing import Optional
from uuid import uuid4

from django import template
from django.utils.html import escapejs
from django.utils.safestring import mark_safe
from plotly.graph_objs._figure import Figure

register = template.Library()


@register.simple_tag()
def bs4_thead(columns: str) -> str:
    ths = "".join([f"<th>{col}</th>" for col in columns.split(",")])
    return mark_safe(f"<thead>{ths}</thead>")


@register.simple_tag()
def bs4_colgroup(columns: str) -> str:
    """Generate a colgroup

    Args:
        columns (str): A comma separated list of integer widths; must sum to 100
    """
    values = list(map(int, columns.split(",")))
    if sum(values) != 100:
        raise ValueError(
            f"colgroup width in `bs4_colgroup` does not sum to 100; got {sum(values)}."
        )
    ths = "".join([f'<col style="width: {v}%;">' for v in values])
    return mark_safe(f"<colgroup>{ths}</colgroup>")


@register.simple_tag()
def bs4_fullrow(text: str, tr_attrs: str = "") -> str:
    """Generate a full-width row.

    Args:
        text (str): Text to be displayed
        tr_attrs (str, default ""): Attributes to add to the wrapping `tr`
    """
    return mark_safe(
        f'<tr {tr_attrs}><td colspan="100%"><p class="text-center mb-0">{text}</p></td></tr>'
    )


@register.simple_tag()
def plotly(fig: Optional[Figure]) -> str:
    """Generate a plotly figure"""
    if fig is None:
        return ""
    id = uuid4()
    return mark_safe(
        dedent(
            f"""
    <div id="{id}"><span class="text-muted">Loading...</span></div>
    <script>
        document.addEventListener("DOMContentLoaded", startup, false);
        function startup () {{
            const data = JSON.parse("{escapejs(fig.to_json())}")
            window.app.renderPlotlyFigure(document.getElementById("{id}"), data);
        }};
    </script>"""
        )
    )
