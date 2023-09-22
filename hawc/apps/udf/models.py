import reversion
from django.conf import settings
from django.db import models
from django.urls import reverse


class UserDefinedForm(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    schema = models.JSONField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="udf_forms_creator"
    )
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="udf_forms")
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    deprecated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("creator", "name"),)
        ordering = ("-last_updated",)

    def get_absolute_url(self):
        return reverse("udf:udf_detail", args=(self.pk,))

    def user_can_edit(self, user):
        return self.creator == user or user in self.editors.all()


reversion.register(UserDefinedForm)
