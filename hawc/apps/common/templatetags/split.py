from django import template

register = template.Library()


@register.simple_tag
def split(string, delimiter=","):
    """Splits a string into a list"""
    return [item.strip() for item in string.split(delimiter)]
