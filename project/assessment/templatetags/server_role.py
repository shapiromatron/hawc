from django import template
from django.conf import settings


register = template.Library()

@register.simple_tag
def server_role():
    return settings.SERVER_ROLE

@register.simple_tag
def server_role_text():
    if settings.SERVER_ROLE == "production":
        return ""
    else:
        return " (%s)" % settings.SERVER_ROLE
