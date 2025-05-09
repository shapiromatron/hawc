"""
Twitter Bootstrap 4 - helper methods
"""

import re
from textwrap import dedent
from uuid import uuid4

from django import template
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
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


def parse_tokens(token, parser) -> dict:
    data = template.base.token_kwargs(token.split_contents()[1:], parser)
    return {k: v.var for k, v in data.items()}


@register.tag(name="alert")
def bs4_alert(parser, token):
    kw = parse_tokens(token, parser)
    nodelist = parser.parse(("endalert",))
    parser.delete_first_token()
    return AlertWrapperNode(nodelist, kw)


class AlertWrapperNode(template.Node):
    dismiss_html = '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'

    def __init__(self, nodelist, kw: dict):
        self.nodelist = nodelist
        self.type = kw.get("type", "danger")
        self.dismiss = kw.get("dismiss", False)
        self.classes = kw.get("classes", "")

    def render(self, context):
        return format_html(
            '<div class="alert alert-{} {}">{}{}</div>',
            self.type,
            self.classes,
            mark_safe(self.dismiss_html) if self.dismiss else "",
            mark_safe(self.nodelist.render(context)),
            "</div>",
        )


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
    <div id="{id}"><span class="is-loading text-muted">Loading, please wait...</span></div>
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


@register.simple_tag
def analytics_card(value, label):
    return mark_safe(
        f"""
        <div class="card box-shadow">
            <div class="card-body">
                <h2 class="m-0 mt-1">{value}</h2>
                <p class="small">{label}</p>
            </div>
        </div>
        """
    )


@register.simple_tag
def list_punctuation(loop, conjunction: str = "or") -> SafeString:
    # return commas between items if > 2, and the appropriate conjunction
    num_items = loop["counter"] + loop["revcounter"] - 1
    if loop["revcounter0"] > 1:
        # if >2 remaining, add commas
        return mark_safe(", ")
    elif loop["revcounter0"] == 1:
        return mark_safe(f"{',' if num_items >= 3 else ''} {conjunction} ")
    return mark_safe("")
