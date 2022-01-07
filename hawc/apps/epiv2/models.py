from django.db import models

# from ..assessment.models import Assessment
from ..study.models import Study
from . import constants, managers


# TODO: set all max_lengths based on the needs of each field
# TODO: set all optional fields to blank=True
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
    description = models.CharField(max_length=128,)

    def __str__(self):
        return self.description


class StudyPopulation(models.Model):
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="study_populations_v2")
    study_design = models.CharField(
        max_length=128, choices=constants.StudyDesign.choices, blank=True
    )
    source = models.CharField(max_length=128, choices=constants.Source.choices)
    age_profile = models.ManyToManyField(AgeProfile, blank=True)
    age_description = models.CharField(
        max_length=128,
        help_text='Select all that apply. Note: do not select "pregnant women" if pregnant women'
        + " are only included as part of a general population sample.",
    )
    sex = models.CharField(default="U", max_length=1, choices=constants.Sex.choices,)
    summary = models.CharField(
        max_length=128,
        verbose_name="Population Summary",
        help_text="Breifly describe the study population (e.g., Women undergoing fertility treatment).",
    )
    countries = models.ManyToManyField(Country, blank=True)
    region = models.CharField(
        max_length=128, blank=True, verbose_name="Other geographic information"
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
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposures"
    )
    measurement_type = models.ManyToManyField(
        MeasurementType, verbose_name="Exposure measurement type"
    )
    biomonitoring_matrix = models.CharField(max_length=128,)
    measurement_timing = models.CharField(
        max_length=128,
        verbose_name="Timing of exposure measurement",
        help_text='If timing is based on something other than age, specify the timing (e.g., start of employment at Factory A). If cross-sectional, enter "cross-sectional"',
    )
    exposure_route = models.CharField(max_length=2, choices=constants.ExposureRoute.choices)
    analytic_method = models.CharField(max_length=128,)
    comments = models.CharField(max_length=128, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class ExposureLevel(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="exposure_levels"
    )
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE)
    exposure_measurement = models.ForeignKey(Exposure, on_delete=models.CASCADE)
    sub_population = models.CharField(
        max_length=128, verbose_name="Sub-population (if relevant)", blank=True
    )
    central_tendency = models.CharField(max_length=128,)
    central_tendency_type = models.CharField(
        max_length=128,
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
    comments = models.CharField(max_length=128, verbose_name="Exposure level comments")
    data_location = models.CharField(max_length=128, help_text="e.g., table number")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Outcome(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="outcomes"
    )
    health_outcome = models.CharField(max_length=128,)
    health_outcome_system = models.CharField(
        max_length=128,
        choices=constants.HealthOutcomeSystem.choices,
        help_text="If multiple cancer types are present, report all types under Cancer.",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class AdjustmentFactor(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="adjustment_factors"
    )
    description = models.CharField(max_length=128,)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class DataExtraction(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation, on_delete=models.CASCADE, related_name="data_extractions"
    )
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE)
    exposure_level = models.ForeignKey(ExposureLevel, on_delete=models.SET_NULL, null=True)
    n = models.PositiveIntegerField()
    effect_estimate_type = models.CharField(
        max_length=128, choices=constants.EffectEstimateType.choices
    )
    effect_estimate = models.CharField(max_length=128,)
    effect_description = models.CharField(max_length=128,)
    measurement_timing = models.CharField(max_length=128,)
    exposure_rank = models.PositiveSmallIntegerField(
        help_text="Rank this comparison group by exposure (lowest exposure group = 1)"
    )
    ci_lcl = models.FloatField(verbose_name="Confidence Interval LCL", blank=True)
    ci_ucl = models.FloatField(verbose_name="Confidence Interval UCL", blank=True)
    sd_or_se = models.FloatField(verbose_name="Standard Deviation or Standard Error", blank=True)
    pvalue = models.CharField(verbose_name="p-value", max_length=128, blank=True)
    significant = models.BooleanField(
        verbose_name="Statistically Significant", choices=constants.SIGNIFICANT_CHOICES
    )
    adjustment_factor = models.ForeignKey(AdjustmentFactor, on_delete=models.SET_NULL, null=True)
    confidence = models.CharField(max_length=128, verbose_name="Study confidence")
    # TODO: data location appears in Exposure Level also. Are both required?
    data_location = models.CharField(max_length=128, help_text="e.g., table number")
    statistical_method = models.CharField(max_length=128,)
    comments = models.CharField(max_length=128, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quantitative data extraction"
