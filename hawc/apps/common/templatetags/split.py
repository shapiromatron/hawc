from django import template

register = template.Library()


@register.simple_tag
def split(string, value):
    """
    Splits a string into a list by some value using python's str.split()

    """
    return string.split(value)
