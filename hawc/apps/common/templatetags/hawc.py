"""
HAWC helper methods
"""

from typing import Any

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe

from ..helper import new_window_a

register = template.Library()


@register.filter
def get(dictionary: dict, key: str):
    """Get a key from a dictionary or dictionary-like object."""
    return dictionary.get(key)


@register.filter
def model_verbose_name(instance):
    return instance._meta.verbose_name


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


@register.simple_tag
def crud_url(app, model, action, id):
    """
    Creates a url via reverse using the appropriate app, model, action, and id

    """
    return reverse(f"{app}:{model}-htmx", args=[id, action])


@register.filter
def hastext(html: str) -> bool:
    """Returns True if text exists after stripping all tags"""
    if html is None:
        return False
    return len(strip_tags(str(html)).strip()) > 0


@register.filter
def percentage(value):
    return f"{value:.0%}"


@register.simple_tag
def split(string, delimiter=","):
    """Splits a string into a list"""
    return [item.strip() for item in string.split(delimiter)]


@register.simple_tag(takes_context=True)
def url_replace(context, *args, **kwargs):
    """
    Add new parameters to a get URL, or removes if None.

    Example usage:
    <a href="?{% url_replace page=paginator.next_page_number %}">

    Source: http://stackoverflow.com/questions/2047622/

    """
    dict_ = context["request"].GET.copy()

    def handle_replace(dict_, key, value):
        dict_[key] = value
        if value is None:
            dict_.pop(key)

    for arg in args:
        for key, value in arg.items():
            handle_replace(dict_, key, value)
    for key, value in kwargs.items():
        handle_replace(dict_, key, value)

    return dict_.urlencode()


@register.simple_tag
def debug_badge(text: str):
    return format_html(
        '<span title="Click to copy text to clipboard" class="badge badge-dark px-1 mx-1 cursor-pointer debug-badge hidden">{}</span>',
        text,
    )


@register.filter
def e_notation(value: str) -> str:
    """Format large and small floating point numbers"""
    if not isinstance(value, int | float):
        return str(value)
    if abs(value) <= 1e-5 or abs(value) >= 1e5:
        return f"{value:.2e}"
    return f"{value:g}"


@register.simple_tag
def label_htmx_url(item) -> str:
    ct = ContentType.objects.get_for_model(item)
    return reverse("assessment:label-item", args=(ct.id, item.id))


@register.simple_tag
def anchor_new_tab() -> str:
    return 'rel="noopener noreferrer" target="_blank"'
