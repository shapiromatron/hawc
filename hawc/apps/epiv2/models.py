from django.db import models

# from ..assessment.models import Assessment
from ..study.models import Study
from . import constants, managers


# TODO: set all max_lengths based on the needs of each field
# TODO: set up managers
class AgeProfile(models.Model):
    # objects = managers.AgeProfileManager()

    name = models.CharField(unique=True, max_length=128,)

    def __str__(self):
        return self.name


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
    description = models.CharField(max_length=128,)

    def __str__(self):
        return self.description


class StudyPopulation(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="study_populations_v2")
    study_design = models.CharField(
        max_length=128, choices=constants.StudyDesign.choices, blank=True, null=True,
    )
    source = models.CharField(
        max_length=128, choices=constants.Source.choices, blank=True, null=True,
    )
    age_profile = models.ManyToManyField(
        AgeProfile,
        blank=True,
        help_text='Select all that apply. Note: do not select "Pregnant women" if pregnant women '
        + "are only included as part of a general population sample",
    )
    sex = models.CharField(default="U", max_length=1, choices=constants.Sex.choices,)
    summary = models.CharField(
        max_length=128,
        verbose_name="Population Summary",
        help_text="Breifly describe the study population (e.g., Women undergoing fertility treatment).",
    )
    countries = models.ManyToManyField(Country, blank=True,)
    region = models.CharField(
        max_length=128, blank=True, null=True, verbose_name="Other geographic information"
    )
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
    name = models.CharField(
        max_length=64,
        help_text="A unique name for this exposure that will help you identify it later.",
    )
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposures"
    )
    measurement_type = models.ManyToManyField(
        MeasurementType, verbose_name="Exposure measurement type", blank=True,
    )
    biomonitoring_matrix = models.CharField(max_length=128,)
    measurement_timing = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="Timing of exposure measurement",
        help_text='If timing is based on something other than age, specify the timing (e.g., start of employment at Factory A). If cross-sectional, enter "cross-sectional"',
    )
    exposure_route = models.CharField(
        max_length=2, choices=constants.ExposureRoute.choices, blank=True, null=True,
    )
    analytic_method = models.CharField(max_length=128, blank=True, null=True,)
    comments = models.CharField(max_length=128, blank=True, null=True,)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ExposureLevel(models.Model):
    name = models.CharField(
        max_length=64,
        help_text="A unique name for this exposure level that will help you identify it later.",
    )
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposure_levels"
    )
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE)
    exposure_measurement = models.ForeignKey(
        Exposure, on_delete=models.CASCADE, blank=True, null=True,
    )
    sub_population = models.CharField(
        max_length=128, verbose_name="Sub-population (if relevant)", blank=True, null=True,
    )
    central_tendency = models.CharField(max_length=128,)
    central_tendency_type = models.CharField(
        max_length=128,
        choices=constants.CentralTendencyType.choices,
        default=constants.CentralTendencyType.MEDIAN,
        verbose_name="Central tendency type (median preferred)",
        blank=True,
        null=True,
    )
    minimum = models.FloatField(blank=True, null=True,)
    maximum = models.FloatField(blank=True, null=True,)
    percentile25 = models.FloatField(blank=True, null=True,)
    percentile75 = models.FloatField(blank=True, null=True,)
    neg_exposure = models.FloatField(
        verbose_name="Percent with negligible exposure",
        help_text="e.g., %% below the LOD",
        blank=True,
        null=True,
    )
    comments = models.CharField(
        max_length=128, verbose_name="Exposure level comments", blank=True, null=True,
    )
    data_location = models.CharField(
        max_length=128, help_text="e.g., table number", blank=True, null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Outcome(models.Model):
    name = models.CharField(
        max_length=64,
        help_text="A unique name for this health outcome that will help you identify it later.",
    )
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="outcomes"
    )
    health_outcome = models.CharField(max_length=128,)
    health_outcome_system = models.CharField(
        max_length=128,
        choices=constants.HealthOutcomeSystem.choices,
        help_text="If multiple cancer types are present, report all types under Cancer.",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AdjustmentFactor(models.Model):
    name = models.CharField(
        max_length=64,
        help_text="A unique name for this adjustment factor that will help you identify it later.",
    )
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="adjustment_factors"
    )
    description = models.CharField(max_length=128, blank=True, null=True,)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DataExtraction(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="data_extractions"
    )
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, blank=True, null=True,)
    exposure_level = models.ForeignKey(
        ExposureLevel, on_delete=models.SET_NULL, blank=True, null=True
    )
    n = models.PositiveIntegerField(blank=True, null=True,)
    effect_estimate_type = models.CharField(
        max_length=128, choices=constants.EffectEstimateType.choices, blank=True, null=True,
    )
    effect_estimate = models.CharField(max_length=128, blank=True, null=True,)
    effect_description = models.CharField(max_length=128, blank=True, null=True,)
    measurement_timing = models.CharField(max_length=128, blank=True, null=True,)
    exposure_rank = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Rank this comparison group by exposure (lowest exposure group = 1)",
    )
    ci_lcl = models.FloatField(verbose_name="Confidence Interval LCL", blank=True, null=True,)
    ci_ucl = models.FloatField(verbose_name="Confidence Interval UCL", blank=True, null=True,)
    sd_or_se = models.FloatField(
        verbose_name="Standard Deviation or Standard Error", blank=True, null=True,
    )
    pvalue = models.CharField(verbose_name="p-value", max_length=128, blank=True, null=True,)
    significant = models.BooleanField(
        verbose_name="Statistically Significant",
        choices=constants.SIGNIFICANT_CHOICES,
        blank=True,
        null=True,
    )
    adjustment_factor = models.ForeignKey(
        AdjustmentFactor, on_delete=models.SET_NULL, blank=True, null=True,
    )
    confidence = models.CharField(
        max_length=128, verbose_name="Study confidence", blank=True, null=True,
    )
    data_location = models.CharField(
        max_length=128, help_text="e.g., table number", blank=True, null=True,
    )
    statistical_method = models.CharField(max_length=128, blank=True, null=True,)
    comments = models.CharField(max_length=128, blank=True, null=True,)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quantitative data extraction"
