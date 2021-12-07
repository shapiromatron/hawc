from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def hastext(html: str) -> bool:
    """Returns True if text exists after stripping all tags"""
    if html is None:
        return False
    return len(strip_tags(str(html)).strip()) > 0
