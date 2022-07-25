from typing import Any, Optional

from django import template

register = template.Library()


@register.simple_tag
def get(obj: Any, attr: str, default: Optional[str] = None):
    """
    Calls the 'get' method on the given object using the provided attribute
    """
    return obj.get(attr, default)
