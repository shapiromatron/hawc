"""
HAWC helper methods
"""
from typing import Any

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


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
