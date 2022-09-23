"""
HAWC helper methods
"""
from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag()
def audit_url(object):
    ct = ContentType.objects.get_for_model(object.__class__)
    return mark_safe(reverse("assessment:log_object_list", args=(ct.pk, object.pk)))
