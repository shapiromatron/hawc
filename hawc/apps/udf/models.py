import reversion
from django.db import models

from ..myuser.models import HAWCUser


class UserDefinedForm(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    schema = models.JSONField()
    creator = models.ForeignKey(HAWCUser, on_delete=models.DO_NOTHING, related_name="created_forms")
    editors = models.ManyToManyField(HAWCUser, blank=True, related_name="editable_forms")
    parent = models.ForeignKey(
        "udf.UserDefinedForm",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    deprecated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["creator", "name"]
        ordering = ["-last_updated"]


reversion.register(UserDefinedForm)
