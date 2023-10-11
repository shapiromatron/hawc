"""
HAWC helper methods
"""
import re
from typing import Any

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe

from ..helper import new_window_a

register = template.Library()


@register.filter
def get(dictionary: dict, key: str):
    """Get a key from a dictionary or dictionary-like object."""
    return dictionary.get(key)


@register.simple_tag
def audit_url(object):
    ct = ContentType.objects.get_for_model(object.__class__)
    return mark_safe(reverse("assessment:log_object_list", args=(ct.pk, object.pk)))


@register.simple_tag
def optional_table_row(name: str, value: Any) -> str:
    if value is not None and value != "":
        return mark_safe(f"<tr><th>{name}</th><td>{value}</td></tr>")
    return ""


@register.simple_tag
def optional_table_list_row(name: str, qs: QuerySet) -> str:
    items = qs.all()
    if items:
        items = ", ".join([f"<span>{item}</span>" for item in items])
        return mark_safe(f"<tr><th>{name}</th><td>{items}</td></tr>")
    return ""


@register.simple_tag
def url_or_span(text: str, url: str | None = None):
    return mark_safe(f'<a href="{url}">{text}</a>') if url else text


@register.simple_tag
def external_url(href: str, text: str) -> str:
    return mark_safe(new_window_a(href, text))


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
