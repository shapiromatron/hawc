"""
Twitter Bootstrap 4 - helper methods
"""
import re
from textwrap import dedent
from uuid import uuid4

from django import template
from django.utils.html import format_html
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
def icon(name: str):
    return format_html('<span class="fa fa-fw {} mr-1" aria-hidden="true"></span>', name)


@register.tag(name="alert")
def bs4_alert(parser, token):
    args = token.contents.split()
    alert_type = args[1] if len(args) > 1 else "danger"
    nodelist = parser.parse(("endalert",))
    parser.delete_first_token()
    return AlertWrapperNode(nodelist, alert_type)


class AlertWrapperNode(template.Node):
    def __init__(self, nodelist, alert_type: str):
        self.nodelist = nodelist
        self.alert_type = alert_type

    def render(self, context):
        return f'<div class="alert alert-{self.alert_type}">{self.nodelist.render(context)}</div>'


@register.simple_tag(name="actions")
def bs4_actions():
    return mark_safe(
        '<div class="actionsMenu dropdown btn-group ml-auto align-self-start flex-shrink-0 pl-2"><a class="btn btn-primary dropdown-toggle" id="actionsDropdownButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Actions</a><div class="dropdown-menu dropdown-menu-right" aria-labelledby="actionsDropdownButton">'
    )


@register.simple_tag(name="endactions")
def bs4_endactions():
    return mark_safe("</div></div>")


_plotly_events = {"dom": "DOMContentLoaded", "htmx": "htmx:afterSettle"}


@register.simple_tag()
def plotly(fig: Figure | None, **kw) -> str:
    """Render a plotly figure

    fig (Figure): the plotly figure to render
    event: (Literal["dom", "htmx"]): the event that should trigger loading plotly. Defaults to
        "dom" when dom is fully loaded. If set to "htmx", will render after htmx settles.
    resizable: (bool, default False). If true, the figure can be resized by the user.
    """
    if fig is None:
        return ""
    id = uuid4()
    config = fig.to_json()
    event = _plotly_events[kw.get("event", "dom")]
    resizable = str(bool(kw.get("resizable", False))).lower()
    func = f'()=>{{window.app.renderPlotlyFigure(document.getElementById("{id}"), {config}, {resizable});}}'
    return mark_safe(
        dedent(
            f"""
    <div id="{id}"><span class="text-muted">Loading...</span></div>
    <script>document.addEventListener("{event}", {func}, false);</script>"""
        )
    )


class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')


@register.filter
def add_class(value, css_class):
    """http://djangosnippets.org/snippets/2253/
    Example call: {{field.name|add_class:"col-md-4"}}"""
    string = str(value)
    match = class_re.search(string)
    if match:
        m = re.search(
            rf"^{css_class}$|^{css_class}\s|\s{css_class}\s|\s{css_class}$",
            match.group(1),
        )
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class, string))
    else:
        return mark_safe(string.replace(">", f' class="{css_class}">'))
    return value
