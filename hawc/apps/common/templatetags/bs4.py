"""
Twitter Bootstrap 4 - helper methods
"""
from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.safestring import mark_safe

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
def audit_url(object):
    # todo move somewhere else
    ct = ContentType.objects.get_for_model(object.__class__)
    return reverse("assessment:log_object_list", args=(ct.pk, object.pk))
