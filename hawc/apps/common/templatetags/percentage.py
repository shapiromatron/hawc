from django import template

register = template.Library()


@register.filter
def percentage(value):
    return f"{value:.0%}"
