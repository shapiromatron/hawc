from django.db import models

# from ..assessment.models import Assessment
from ..study.models import Study
from . import constants, managers


class AgeProfile(models.Model):
    # objects = managers.AgeProfileManager()

    name = models.CharField(
        unique=True,
        max_length=128,
        help_text='Select all that apply. Note: do not select "Pregnant women" if pregnant women '
        + "are only included as part of a general population sample",
    )


class Country(models.Model):
    objects = managers.CountryManager()

    code = models.CharField(blank=True, max_length=2)
    name = models.CharField(unique=True, max_length=64)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class MeasurementType(models.Model):
    description = models.CharField()

    def __str__(self):
        return self.name


class StudyPopulation(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="study_populations")
    study_design = models.CharField(choices=constants.StudyDesign.choices, blank=True)
    source = models.CharField(choices=constants.Source.choices)
    age_profile = models.ManyToManyField(AgeProfile, blank=True)
    age_description = models.CharField(help_text="")
    sex = models.CharField(default="U", choices=constants.Sex.choices,)
    summary = models.CharField()
    countries = models.ManyToManyField(Country, blank=True)
    region = models.CharField(max_length=128, blank=True)
    participant_n = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Chemical(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="chemicals"
    )
    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Criteria(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="criteria"
    )

    name = models.CharField(max_length=64)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Exposure(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposures"
    )
    measurement_type = models.ManyToManyField(MeasurementType)
    measurement_timing = models.CharField()
    exposure_route = models.CharField()
    analytic_method = models.CharField()
    comments = models.CharField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class ExposureLevel(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposure_levels"
    )
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
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="outcomes"
    )
    health_outcome = models.CharField()
    health_outcome_system = models.CharField()
    measurement_timing = (
        models.CharField()
    )  # TODO: prototype had outcome measurement timing as a separate table, is that necessary?
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class AdjustmentFactor(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="adjustment_factors"
    )
    description = models.CharField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class DataExtraction(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="data_extractions"
    )
    outcome = models.ForeignKey(Outcome, on_delete=models.SET_NULL)
    exposure = models.ForeignKey(Exposure, on_delete=models.SET_NULL)
    n = models.PositiveIntegerField()
    effect_estimate_type = models.CharField(choices=constants.EffectEstimateType.choices)
    effect_estimate = models.CharField()
    effect_description = models.CharField()
    exposure_rank = models.PositiveSmallIntegerField()
    # TODO: what are these fields
    # CI LCL
    # CI UCL
    # SD or SE
    pvalue = models.FloatField()
    # TODO: this is derived from the p-value (p-value>0.05). Necessary to have as a field?
    significant = models.BooleanField()
    adjustment_factor = models.ForeignKey(AdjustmentFactor, on_delete=models.SET_NULL)
    confidence = models.CharField()
    location = models.CharField()
    statistical_method = models.CharField()
    comments = models.CharField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quantitative data extraction"
