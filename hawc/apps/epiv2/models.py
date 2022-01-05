from django.db import models

from ..assessment.models import Assessment
from ..study.models import Study
from . import constants, managers


class Country(models.Model):
    objects = managers.CountryManager()

    code = models.CharField(blank=True, max_length=2)
    name = models.CharField(unique=True, max_length=64)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class StudyPopulation(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="study_populations")
    study_design = models.CharField()
    source = models.CharField()
    age_category = models.ManyToManyField()
    age_description = models.CharField()
    sex = models.PositiveSmallIntegerField()
    summary = models.CharField()
    study_id = models.ForeignKey()
    countries = models.ManyToManyField(Country, blank=True)
    region = models.CharField(max_length=128, blank=True)
    participant_n = models.PositiveIntegerField()
    criteria = models.ManyToManyField()

    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Chemical(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Exposure(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Outcome(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
