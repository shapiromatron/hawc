from django.db import models

# from ..assessment.models import Assessment
from ..study.models import Study
from . import constants, managers


# TODO: set up managers
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
        return self.description


class StudyPopulation(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="study_populations")
    study_design = models.CharField(choices=constants.StudyDesign.choices, blank=True)
    source = models.CharField(choices=constants.Source.choices)
    age_profile = models.ManyToManyField(AgeProfile, blank=True)
    age_description = models.CharField(
        help_text='Select all that apply. Note: do not select "pregnant women" if pregnant women'
        + " are only included as part of a general population sample."
    )
    sex = models.CharField(default="U", choices=constants.Sex.choices,)
    summary = models.CharField(
        verbose_name="Population Summary",
        help_text="Breifly describe the study population (e.g., Women undergoing fertility treatment).",
    )
    countries = models.ManyToManyField(Country, blank=True)
    region = models.CharField(max_length=128, blank=True)
    participant_n = models.PositiveIntegerField(
        verbose_name="Overall study population N",
        help_text="Enter the total number of participants enrolled in the study (after exclusions).\n"
        + "Note: Sample size for specific result can be extracted in qualitative data extraction",
    )
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

    class Meta:
        verbose_name = "Inclusion/exclusion criteria"

    def __str__(self):
        return self.name


class Exposure(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposures"
    )
    measurement_type = models.ManyToManyField(
        MeasurementType, verbose_name="Exposure measurement type"
    )
    biomonitoring_matrix = models.CharField()
    measurement_timing = models.CharField(
        verbose_name="Timing of exposure measurement",
        help_text='If timing is based on something other than age, specify the timing (e.g., start of employment at Factory A). If cross-sectional, enter "cross-sectional"',
    )
    exposure_route = models.CharField(choices=constants.ExposureRoute.choices)
    analytic_method = models.CharField()
    comments = models.CharField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class ExposureLevel(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposure_levels"
    )
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE)
    exposure_measurement = models.ForeignKey(Exposure, on_delete=models.CASCADE)
    sub_population = models.CharField(verbose_name="Sub-population (if relevant)", blank=True)
    central_tendency = models.CharField()
    central_tendency_type = models.CharField(
        choices=constants.CentralTendencyType.choices,
        default=constants.CentralTendencyType.MEDIAN,
        verbose_name="Central tendency type (median preferred)",
    )
    minimum = models.FloatField()
    maximum = models.FloatField()
    percentile25 = models.FloatField()
    percentile75 = models.FloatField()
    neg_exposure = models.FloatField(
        verbose_name="Percent with negligible exposure", help_text="e.g., %% below the LOD"
    )
    comments = models.CharField(verbose_name="Exposure level comments")
    data_location = models.CharField(help_text="e.g., table number")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Outcome(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="outcomes"
    )
    health_outcome = models.CharField()
    health_outcome_system = models.CharField(
        choices=constants.HealthOutcomeSystem.choices,
        help_text="If multiple cancer types are present, report all types under Cancer.",
    )
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
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    exposure_level = models.ForeignKey(ExposureLevel, on_delete=models.SET_NULL)
    n = models.PositiveIntegerField()
    effect_estimate_type = models.CharField(choices=constants.EffectEstimateType.choices)
    effect_estimate = models.CharField()
    effect_description = models.CharField()
    measurement_timing = models.CharField()
    exposure_rank = models.PositiveSmallIntegerField(
        help_text="Rank this comparison group by exposure (lowest exposure group = 1)"
    )
    ci_lcl = models.FloatField(blank=True)
    ci_ucl = models.FloatField(blank=True)
    sd_or_se = models.FloatField(blank=True)
    pvalue = models.CharField(blank=True)
    significant = models.BooleanField(
        verbose_name="Statistically Significant", choices=constants.SIGNIFICANT_CHOICES
    )
    adjustment_factor = models.ForeignKey(AdjustmentFactor, on_delete=models.SET_NULL)
    confidence = models.CharField(verbose_name="Study confidence")
    # TODO: data location appears in Exposure Level also. Are both required?
    data_location = models.CharField(help_text="e.g., table number")
    statistical_method = models.CharField()
    comments = models.CharField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quantitative data extraction"
