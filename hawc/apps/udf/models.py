import reversion
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from ..assessment.models import Assessment
from ..lit.models import ReferenceFilterTag


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


class ModelBinding(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="udf_bindings"
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, choices=)
    form = models.ForeignKey(UserDefinedForm, on_delete=models.CASCADE, related_name="models")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="udf_models"
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = (models.Index(fields=["assessment", "content_type"]),)
        unique_together = (("assessment", "content_type"),)


class TagBinding(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="udf_tag_bindings"
    )
    tag = models.ForeignKey(ReferenceFilterTag, on_delete=models.CASCADE, related_name="udf_forms")
    form = models.ForeignKey(UserDefinedForm, on_delete=models.CASCADE, related_name="tags")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="udf_tags"
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = (models.Index(fields=["assessment", "tag"]),)
        unique_together = (("assessment", "tag"),)


reversion.register(TagBinding)
reversion.register(ModelBinding)
reversion.register(UserDefinedForm)
