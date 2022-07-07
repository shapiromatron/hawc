from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def crud_url(app, model, action, id):
    """
    Creates a url via reverse using the appropriate app, model, action, and id

    """
    return reverse(f"{app}:{model}-{action}", args=[id])
