from django.db import models
from ..assessment.models import Assessment
from ..study.models import Study
from . import constants, managers


class AgeProfile(models.Model):
    # objects = managers.AgeProfileManager()

    name = models.CharField(unique=True, max_length=128)


class Country(models.Model):
    objects = managers.CountryManager()

    code = models.CharField(blank=True, max_length=2)
    name = models.CharField(unique=True, max_length=64)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class Chemical(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Criteria(models.Model):
    name = models.CharField(max_length=64)


class Exposure(models.Model):
    measurement_type = models.ManyToManyField()
    measurement_timing = models.CharField()
    exposure_route = models.CharField()
    analytic_method = models.CharField()
    comments = models.CharField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class ExposureLevel(models.Model):
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE)
    exposure_measurement = models.ForeignKey(Exposure, on_delete=models.CASCADE)
    sub_population = models.CharField()
    # TODO: should some of this be separated into another model?
    central_tendency = models.CharField()
    central_tendency_type = models.CharField()
    minimum = models.FloatField()
    maximum = models.FloatField()
    percentile25 = models.FloatField()
    percentile75 = models.FloatField()
    neg_exposure = models.FloatField()
    comments = models.CharField()
    data_location = models.CharField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Outcome(models.Model):
    health_outcome = models.CharField()
    health_outcome_system = models.CharField()
    measurement_timing = (
        models.CharField()
    )  # TODO: prototype had outcome measurement timing as a separate table, is that necessary?
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class AdjustmentFactor(models.Model):
    description = models.CharField()


class StudyPopulation(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="study_populations")
    study_design = models.CharField(choices=constants.StudyDesign.choices, blank=True)
    source = models.CharField(choices=constants.Source.choices)
    age_profile = models.ManyToManyField(AgeProfile, blank=True)
    age_description = models.CharField()
    sex = models.CharField(default="U", choices=constants.Sex.choices,)
    summary = models.CharField()
    countries = models.ManyToManyField(Country, blank=True)
    region = models.CharField(max_length=128, blank=True)
    participant_n = models.PositiveIntegerField()
    criteria = models.ManyToManyField(Criteria, blank=True)
    chemicals = models.ManyToManyField(Chemical, blank=True)
    exposures = models.ManyToManyField(Exposure, blank=True)
    outcomes = models.ManyToManyField(Outcome, blank=True)
    adjustment_factors = models.ManyToManyField(AdjustmentFactor, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
