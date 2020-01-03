from django import template

register = template.Library()


@register.filter
def percentage(value):
    return '{0:.0%}'.format(value)
