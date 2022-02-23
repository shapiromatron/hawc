from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def split(string, value):
    """
    Splits a string into a list by some value using python's str.split()

    """
    return string.split(value)
