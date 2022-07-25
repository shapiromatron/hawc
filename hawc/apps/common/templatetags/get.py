from django import template

register = template.Library()


@register.simple_tag
def get(obj, attr):
    """
    Calls the 'get' method on the given object using the provided attribute
    """
    return obj.get(attr)
