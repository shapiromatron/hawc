import reversion
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from ..assessment.models import DSSTox
from ..epi.models import Country
from ..study.models import Study
from . import constants, managers


class Design(models.Model):
    objects = managers.DesignManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="designs")
    summary = models.CharField(
        max_length=128,
        verbose_name="Population Summary",
        help_text="Breifly describe the study population (e.g., Women undergoing fertility treatment).",
    )
    study_name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="Study name (if applicable)",
        help_text="Typically available for cohorts. Abbreviations provided in the paper are fine",
    )
    study_design = models.CharField(max_length=2, choices=constants.StudyDesign.choices, blank=True)
    source = models.CharField(max_length=2, choices=constants.Source.choices, blank=True)
    age_profile = ArrayField(
        models.CharField(max_length=2, choices=constants.AgeProfile.choices),
        blank=True,
        help_text='Select all that apply. Note: do not select "Pregnant women" if pregnant women are only included as part of a general population sample',
        verbose_name="Population age category",
    )
    age_description = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Population age details",
    )
    sex = models.CharField(default=constants.Sex.BOTH, max_length=1, choices=constants.Sex.choices)
    race = models.CharField(max_length=128, blank=True, verbose_name="Population race/ethnicity")
    participant_n = models.PositiveIntegerField(
        verbose_name="Overall study population N",
        help_text="Enter the total number of participants enrolled in the study (after exclusions).\nNote: Sample size for specific result can be extracted in qualitative data extraction",
    )
    years_enrolled = models.CharField(
        max_length=32, verbose_name="Year(s) of enrollment", blank=True
    )
    years_followup = models.CharField(
        max_length=32, verbose_name="Year(s) or length of follow-up", blank=True
    )
    countries = models.ManyToManyField(
        Country,
        blank=True,
        related_name="epiv2_designs",
    )
    region = models.CharField(
        max_length=128, blank=True, verbose_name="Other geographic information"
    )
    criteria = models.TextField(blank=True, verbose_name="Inclusion/Exclusion Criteria")
    susceptibility = models.TextField(blank=True, verbose_name="Susceptibility")
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study"

    class Meta:
        verbose_name = "Study Population"
        verbose_name_plural = "Study Populations"
        ordering = ("id",)

    def get_assessment(self):
        return self.study.get_assessment()

    def get_study(self):
        return self.study

    def get_absolute_url(self):
        return reverse("epiv2:design_detail", args=(self.pk,))

    def get_update_url(self):
        return reverse("epiv2:design_update", args=(self.pk,))

    def get_delete_url(self):
        return reverse("epiv2:design_delete", args=(self.pk,))

    def get_age_profile_display(self):
        return ", ".join(constants.AgeProfile(ap).label for ap in self.age_profile)

    def __str__(self):
        return f"{self.summary}"


class Chemical(models.Model):
    objects = managers.ChemicalManager()

    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name="chemicals")
    name = models.CharField(
        max_length=128,
        help_text="This field is commonly used in visualizations, so consider using a common acronym, e.g., BPA instead of Bisphenol A",
    )
    dsstox = models.ForeignKey(
        DSSTox,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="DSSTox substance identifier",
        help_text="""
        <a href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DSSTox</a>
        substance identifier (recommended). When using an identifier, chemical name and CASRN are
        standardized using the DTXSID.
        """,
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.design.get_assessment()

    def get_study(self):
        return self.design.get_study()

    def __str__(self):
        return self.name

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self


class Exposure(models.Model):
    objects = managers.ExposureManager()

    name = models.CharField(
        max_length=128,
        help_text="A unique name for this exposure that will help you identify it later.",
    )
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name="exposures")
    measurement_type = models.CharField(
        max_length=2,
        verbose_name="Exposure measurement type",
        choices=constants.MeasurementType.choices,
    )
    biomonitoring_matrix = models.CharField(
        max_length=3, choices=constants.BiomonitoringMatrix.choices, blank=True
    )
    biomonitoring_source = models.CharField(
        max_length=2, choices=constants.BiomonitoringSource.choices, blank=True
    )
    measurement_timing = models.CharField(
        max_length=256,
        verbose_name="Timing of exposure measurement",
        help_text='If timing is based on something other than age, specify the timing (e.g., start of employment at Factory A). If cross-sectional, enter "cross-sectional"',
    )
    exposure_route = models.CharField(
        max_length=2, choices=constants.ExposureRoute.choices, blank=True
    )
    measurement_method = models.TextField(blank=True, verbose_name="Exposure measurement method")
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.design.get_assessment()

    def get_study(self):
        return self.design.get_study()

    def __str__(self):
        return self.name

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self


class ExposureLevel(models.Model):
    objects = managers.ExposureLevelManager()

    name = models.CharField(
        max_length=64,
        help_text="A unique name for this exposure level that will help you identify it later.",
    )
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name="exposure_levels")
    chemical = models.ForeignKey(Chemical, on_delete=models.CASCADE)
    exposure_measurement = models.ForeignKey(Exposure, on_delete=models.CASCADE)
    sub_population = models.CharField(
        max_length=128, verbose_name="Sub-population", blank=True, help_text="(if relevant)"
    )
    median = models.FloatField(blank=True, null=True)
    mean = models.FloatField(blank=True, null=True)
    variance = models.FloatField(blank=True, null=True)
    variance_type = models.PositiveSmallIntegerField(
        choices=constants.VarianceType.choices, default=constants.VarianceType.NONE
    )
    units = models.CharField(max_length=128, blank=True, null=True)
    ci_lcl = models.FloatField(blank=True, null=True, verbose_name="Lower CI")
    percentile_25 = models.FloatField(blank=True, null=True, verbose_name="25th Percentile")
    percentile_75 = models.FloatField(blank=True, null=True, verbose_name="75th Percentile")
    ci_ucl = models.FloatField(blank=True, null=True, verbose_name="Upper CI")
    ci_type = models.CharField(
        max_length=3,
        choices=constants.ConfidenceIntervalType.choices,
        default=constants.ConfidenceIntervalType.RNG,
        verbose_name="Confidence interval type",
    )
    neg_exposure = models.FloatField(
        verbose_name="Percent with negligible exposure",
        help_text="e.g., % below the LOD",
        blank=True,
        null=True,
    )
    data_location = models.CharField(max_length=128, help_text="e.g., table number", blank=True)
    comments = models.TextField(verbose_name="Exposure level comments", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.design.get_assessment()

    def get_study(self):
        return self.design.get_study()

    def __str__(self):
        return self.name

    def get_quantitative_value(self):
        value = "NR"
        if self.median is not None:
            value = f"{self.median}"
        elif self.mean is not None:
            value = f"{self.mean}"
        if self.ci_lcl is not None and self.ci_ucl is not None:
            value += f" [{self.ci_lcl}, {self.ci_ucl}]"
        if self.units:
            value += f" {self.units}"
        return value

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self


class Outcome(models.Model):
    objects = managers.OutcomeManager()

    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name="outcomes")
    endpoint = models.CharField(
        max_length=128,
        help_text="A unique name for this health outcome that will help you identify it later.",
    )
    health_outcome = models.CharField(max_length=128)
    health_outcome_system = models.CharField(
        max_length=2,
        choices=constants.HealthOutcomeSystem.choices,
        help_text="If multiple cancer types are present, report all types under Cancer.",
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.design.get_assessment()

    def get_study(self):
        return self.design.get_study()

    def __str__(self):
        return self.endpoint

    def clone(self):
        self.id = None
        self.endpoint = f"{self.endpoint} (2)"
        self.save()
        return self


class AdjustmentFactor(models.Model):
    objects = managers.AdjustmentFactorManager()

    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name="adjustment_factors")
    name = models.CharField(
        max_length=32,
        help_text="A unique name for this adjustment factor that will help you identify it later.",
    )
    description = models.CharField(max_length=128, help_text="Comma separated list")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.design.get_assessment()

    def get_study(self):
        return self.design.get_study()

    def __str__(self):
        return self.name

    def clone(self):
        self.id = None
        self.name = f"{self.name} (2)"
        self.save()
        return self


class DataExtraction(models.Model):
    objects = managers.DataExtractionManager()

    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name="data_extractions")
    outcome = models.ForeignKey(Outcome, related_name="outcomes", on_delete=models.CASCADE)
    exposure_level = models.ForeignKey(
        ExposureLevel, related_name="exposure_levels", on_delete=models.CASCADE
    )
    sub_population = models.CharField(
        max_length=128, blank=True, help_text="Use N/A if sub population is not relevant"
    )
    outcome_measurement_timing = models.CharField(max_length=128, blank=True)
    effect_estimate = models.FloatField()
    effect_estimate_type = models.CharField(
        max_length=3, choices=constants.EffectEstimateType.choices
    )
    variance = models.FloatField(blank=True, null=True)
    variance_type = models.PositiveSmallIntegerField(
        choices=constants.VarianceType.choices, default=constants.VarianceType.NONE
    )
    n = models.PositiveIntegerField(blank=True, null=True)
    ci_lcl = models.FloatField(verbose_name="Lower CI", blank=True, null=True)
    ci_ucl = models.FloatField(verbose_name="Upper CI", blank=True, null=True)
    ci_type = models.CharField(
        max_length=3,
        choices=constants.ConfidenceIntervalType.choices,
        default=constants.ConfidenceIntervalType.RNG,
        verbose_name="Confidence interval type",
    )
    p_value = models.CharField(verbose_name="p-value", max_length=8, blank=True)
    significant = models.PositiveSmallIntegerField(
        verbose_name="Statistically Significant",
        choices=constants.Significant.choices,
        default=constants.Significant.NR,
    )
    adjustment_factor = models.ForeignKey(
        AdjustmentFactor,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    confidence = models.CharField(max_length=128, verbose_name="Study confidence", blank=True)
    data_location = models.CharField(max_length=128, help_text="e.g., table number", blank=True)
    exposure_rank = models.PositiveSmallIntegerField(
        default=0,
        help_text="Rank this comparison group by exposure (lowest exposure group = 1); used for sorting in visualizations",
    )
    effect_description = models.TextField(
        blank=True,
        verbose_name="Effect estimate description",
        help_text="Description of the effect estimate with units, including comparison group if applicable",
    )
    statistical_method = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quantitative data extraction"
        ordering = ("id",)

    def get_assessment(self):
        return self.design.get_assessment()

    def get_study(self):
        return self.design.get_study()

    def get_estimate_value(self) -> str:
        value = f"{self.effect_estimate}" if self.effect_estimate is not None else "-"
        if self.ci_lcl and self.ci_ucl:
            value += f" [{self.ci_lcl}, {self.ci_ucl}]"
        return value

    def clone(self):
        self.id = None
        self.save()
        return self


reversion.register(Design, follow=("countries",))
reversion.register(Chemical)
reversion.register(Exposure)
reversion.register(ExposureLevel)
reversion.register(Outcome)
reversion.register(AdjustmentFactor)
reversion.register(DataExtraction)
