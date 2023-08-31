import reversion
from django.db import models

from ..myuser.models import HAWCUser


# TODO: is this a good name? i changed it from dynamic form because it makes the naming scheme weird
# for the actual form class (DynamicFormForm)
class CustomDataExtraction(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    schema = models.JSONField()
    creator = models.ForeignKey(
        HAWCUser, on_delete=models.SET_NULL, null=True, related_name="created_forms"
    )
    editors = models.ManyToManyField(HAWCUser, blank=True, related_name="editable_forms")
    parent_form = models.ForeignKey(
        "form_library.CustomDataExtraction",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="child_forms",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


reversion.register(CustomDataExtraction)
