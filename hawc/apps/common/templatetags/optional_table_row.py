from typing import Any

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def optional_table_row(name: str, value: Any) -> str:
    if value is not None and value != "":
        return mark_safe(f"<tr><th>{name}</th><td>{escape(value)}</td></tr>")
    return ""
