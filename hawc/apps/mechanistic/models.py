import reversion
from django.db import models
from django.urls import reverse

from ..study.models import Study
from . import constants, managers


class Experiment(models.Model):
    objects = managers.ExperimentManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="mechanistic_experiments")

    name = models.CharField(
        max_length=128,
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study"

    TEXT_CLEANUP_FIELDS = (
        "name",
        "comments",
    )

    class Meta:
        verbose_name = "Mechanistic Experiment"
        verbose_name_plural = "Mechanistic Experiments"
        ordering = ("id",)

    def get_assessment(self):
        return self.study.get_assessment()

    def get_study(self):
        return self.study

    def get_absolute_url(self):
        return reverse("mechanistic:experiment_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("mechanistic:experiment_update", args=(self.pk,))

    def get_delete_url(self):
        return reverse("mechanistic:experiment_delete", args=(self.pk,))

    def __str__(self):
        return f"{self.name}"


reversion.register(Experiment)
