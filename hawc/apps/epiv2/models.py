import reversion
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse

from ..assessment.models import DSSTox
from ..common.helper import SerializerHelper
from ..common.models import NumericTextField
from ..epi.models import Country
from ..study.models import Study
from . import constants, managers


class Design(models.Model):
    objects = managers.DesignManager()

    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="designs")
    summary = models.CharField(
        max_length=128,
        verbose_name="Population Summary",
        help_text="Briefly describe the study population. Try to capture anything outside a typical general population samples (e.g.,people with a specific health condition, specific environments [e.g., assisted living facility, farmers, etc.], exposure scenario, etc. This field may be used in visualizations as a summary of the study, so it is important to be consistent within the assessment.",
    )
    study_name = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Study name (if applicable)",
        help_text="Study name assigned by authors. Typically available for cohorts.",
    )
    study_design = models.CharField(
        max_length=2,
        choices=constants.StudyDesign,
        help_text='Select the most appropriate design from the list. If more than one study design applies (e.g., a cohort with cross-sectional analyses of baseline measures), can either a) select one design ("cohort") and clarify different timing in remaining extraction or b) select "other" and provide details in comments.',
    )
    source = models.CharField(max_length=2, choices=constants.Source)
    age_profile = ArrayField(
        models.CharField(max_length=2, choices=constants.AgeProfile),
        help_text='Select all that apply. Note: do not select "Pregnant women" if pregnant women are only included as part of a general population sample',
        verbose_name="Population age category",
    )
    age_description = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Population age details",
    )
    sex = models.CharField(default=constants.Sex.BOTH, max_length=1, choices=constants.Sex)
    race = models.CharField(max_length=128, blank=True, verbose_name="Population race/ethnicity")
    participant_n = models.PositiveIntegerField(
        verbose_name="Overall study population N",
        help_text="Enter the total number of participants enrolled in the study (after exclusions). Note: Sample size for specific result can be extracted in qualitative data extraction",
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
    susceptibility = models.TextField(
        blank=True,
        verbose_name="Susceptibility",
        help_text="Note whether the study presents information for potentially susceptible or vulnerable populations or sub-populations, such as pregnant women or residents of environmental justice communities.",
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    BREADCRUMB_PARENT = "study"

    TEXT_CLEANUP_FIELDS = (
        "summary",
        "study_name",
        "age_description",
        "race",
        "years_enrolled",
        "years_followup",
        "region",
    )

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
        help_text=DSSTox.help_text(),
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    TEXT_CLEANUP_FIELDS = ("name",)

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
    measurement_type = ArrayField(
        models.CharField(max_length=64),
        help_text='Select the most appropriate type from the list. If a study includes multiples exposure measurement types but they are analyzed with outcomes separately, create a separate entry for each. If more than one type are combined for analysis with an outcome, you can select multiple options from the list. "Occupational" should be used when the exposure is based on job duties, etc. (i.e., not occupational exposure measured by biomarkers or air).',
        verbose_name="Exposure measurement types",
    )
    biomonitoring_matrix = models.CharField(
        max_length=3, choices=constants.BiomonitoringMatrix, blank=True
    )
    biomonitoring_source = models.CharField(
        max_length=2, choices=constants.BiomonitoringSource, blank=True
    )
    measurement_timing = models.CharField(
        max_length=256,
        blank=True,
        verbose_name="Timing of exposure measurement",
        help_text='Enter age or other timing (e.g., start of employment, baseline). If cross-sectional, enter "cross-sectional".',
    )
    exposure_route = models.CharField(
        max_length=2,
        choices=constants.ExposureRoute,
        default=constants.ExposureRoute.UNKNOWN,
        help_text='Select the most appropriate route. In most cases, biomarkers will be "Unknown/Total" unless a clear exposure source is known.',
    )
    measurement_method = models.TextField(
        blank=True,
        verbose_name="Exposure measurement method",
        help_text="Briefly state the method used to measure exposure (e.g., laboratory analytic method, job exposure matrix, etc.)",
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    TEXT_CLEANUP_FIELDS = (
        "name",
        "measurement_timing",
    )

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
    chemical = models.ForeignKey(
        Chemical, on_delete=models.CASCADE, help_text="Select from chemicals entered above."
    )
    exposure_measurement = models.ForeignKey(
        Exposure,
        on_delete=models.CASCADE,
        help_text="Select from exposure measurement entered above.",
    )
    sub_population = models.CharField(
        max_length=128,
        verbose_name="Sub-population",
        blank=True,
        help_text="Specify if the exposure levels are reported for a sub-group within the study population (e.g., by case or exposure status, sex, etc.)",
    )
    median = models.FloatField(blank=True, null=True)
    mean = models.FloatField(blank=True, null=True)
    variance = models.FloatField(blank=True, null=True)
    variance_type = models.PositiveSmallIntegerField(
        choices=constants.VarianceType,
        default=constants.VarianceType.NA,
        verbose_name="Type of variance estimate",
        help_text="Specify which measure of variation was reported from list",
    )
    units = models.CharField(max_length=128, blank=True)
    ci_lcl = NumericTextField(
        max_length=16,
        blank=True,
        verbose_name="Lower interval",
        help_text=f"Lower value of whichever range is selected in Lower/Upper interval type. {NumericTextField.generic_help_text}",
    )
    percentile_25 = NumericTextField(
        max_length=16,
        blank=True,
        verbose_name="25th Percentile",
        help_text=NumericTextField.generic_help_text,
    )
    percentile_75 = NumericTextField(
        max_length=16,
        blank=True,
        verbose_name="75th Percentile",
        help_text=NumericTextField.generic_help_text,
    )
    ci_ucl = NumericTextField(
        max_length=16,
        blank=True,
        verbose_name="Upper interval",
        help_text=f"Upper value of whichever range is selected in Lower/Upper interval type. {NumericTextField.generic_help_text}",
    )
    ci_type = models.CharField(
        max_length=3,
        choices=constants.ConfidenceIntervalType,
        default=constants.ConfidenceIntervalType.NA,
        verbose_name="Lower/upper interval type",
    )
    negligible_exposure = models.CharField(
        verbose_name="Percent with negligible exposure",
        help_text="Enter the percent of the population without measureable exposure. For biomarkers and other lab results, this will generally be the percent below the LOD or LOQ. Occupational studies may report the percent unexposed. The field is free text so elaboration on the meaning of the number can be provided.",
        blank=True,
        max_length=64,
    )
    data_location = models.CharField(max_length=128, help_text="e.g., table number", blank=True)
    comments = models.TextField(verbose_name="Exposure level comments", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    TEXT_CLEANUP_FIELDS = (
        "name",
        "sub_population",
        "units",
        "negligible_exposure",
        "data_location",
    )

    class Meta:
        ordering = ("id",)

    def get_assessment(self):
        return self.design.get_assessment()

    def get_study(self):
        return self.design.get_study()

    def __str__(self):
        return self.name

    def exposure_html(self):
        default_value = value = "-"
        if self.median is not None:
            value = f"{self.median}"
        elif self.mean is not None:
            value = f"{self.mean}"
        if value != default_value and self.units:
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
    system = models.CharField(
        max_length=2,
        choices=constants.HealthOutcomeSystem,
        help_text="Select the most relevant system from the drop down menu. If more than one system is applicable refer to assessment team instructions.",
    )
    effect = models.CharField(
        max_length=128,
        help_text="The health effect of interest. Effect is generally broader than the Endpoint/Outcome and may represent multiple endpoints (e.g., Serum lipids, Asthma, Cognition). However, if there is not a finer categorization, they may be the same. Use controlled vocabulary when available.",
    )
    effect_detail = models.CharField(
        max_length=128,
        blank=True,
        help_text="Optional. If additional specification to the Effect is needed, it can be entered here (e.g., IQ).",
    )
    endpoint = models.CharField(
        verbose_name="Endpoint/Outcome",
        max_length=128,
        help_text="A unique name for the specific endpoint/outcome being measured. The endpoint is generally more specific than the effect (e.g., total cholesterol, incident asthma within the previous year, WISC-IV full scale). Use controlled vocabulary when available.",
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    TEXT_CLEANUP_FIELDS = (
        "effect",
        "effect_detail",
        "endpoint",
    )

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
        help_text='A unique name for this adjustment set that will help you identify it later. It may be descriptive or a dummy variable ("A").',
    )
    description = models.CharField(
        max_length=512,
        help_text='Enter the list of covariates in the model, separated by commas. These can be brief and ideally entered uniformly across studies when possible. Additional detail can be added in the comments or in study evaluation (e.g., enter "smoking" for consistency instead of "pack-years")',
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    TEXT_CLEANUP_FIELDS = (
        "name",
        "description",
    )

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
    outcome = models.ForeignKey(
        Outcome,
        related_name="outcomes",
        on_delete=models.CASCADE,
        help_text="Select from endpoints entered above",
    )
    exposure_level = models.ForeignKey(
        ExposureLevel,
        related_name="exposure_levels",
        on_delete=models.CASCADE,
        help_text="Select from exposure levels entered above",
    )
    sub_population = models.CharField(
        max_length=128,
        blank=True,
        help_text="Specify if the result is specific to a sub-group within the study population. Leave blank if the result applies to the full population.",
    )
    outcome_measurement_timing = models.CharField(
        max_length=128,
        blank=True,
        help_text='Enter age or other timing (e.g., X years follow-up) for measurement of outcome. If cross-sectional, enter "cross-sectional".',
    )
    effect_estimate_type = models.CharField(
        max_length=128,
        blank=True,
    )
    effect_estimate = models.FloatField()
    ci_lcl = models.FloatField(verbose_name="Lower bound", blank=True, null=True)
    ci_ucl = models.FloatField(verbose_name="Upper bound", blank=True, null=True)
    ci_type = models.CharField(
        max_length=3,
        choices=constants.ConfidenceIntervalType,
        default=constants.ConfidenceIntervalType.P95,
        verbose_name="Lower/upper bound type",
    )
    units = models.CharField(max_length=128, blank=True)
    variance_type = models.PositiveSmallIntegerField(
        choices=constants.VarianceType,
        default=constants.VarianceType.NA,
        verbose_name="Type of variance estimate",
        help_text="Specify which measure of variation was reported from list",
    )
    variance = models.FloatField(blank=True, null=True)
    n = models.PositiveIntegerField(blank=True, null=True)
    p_value = models.CharField(verbose_name="p-value", max_length=8, blank=True)
    significant = models.PositiveSmallIntegerField(
        verbose_name="Statistically Significant",
        choices=constants.Significant,
        default=constants.Significant.NR,
    )
    group = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Results group",
        help_text='If a set of results are linked (e.g., results for categories of exposure), each one is entered as a separate entry in the form. This field should be used to link the results. All linked results should have the same value for this field, and it should be unique to those results. The text can be descriptive (e.g., "Quartiles for PFNA and Asthma incidence") or a dummy variable ("Group 1").',
    )
    exposure_rank = models.PositiveSmallIntegerField(
        default=0,
        help_text="If a set of results are linked, use this field to order them (helpful for sorting in visualizations). Rank the comparison groups in the order you would want them to appear (e.g., lowest exposure group=1).",
    )
    exposure_transform = models.CharField(max_length=32, blank=True)
    outcome_transform = models.CharField(max_length=32, blank=True)
    factors = models.ForeignKey(
        AdjustmentFactor,
        verbose_name="Adjustment factors",
        help_text="Select from adjustment sets entered above",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    confidence = models.CharField(
        max_length=128,
        verbose_name="Study confidence",
        blank=True,
        help_text="Enter the overall study confidence rating for the specific endpoint being extracted",
    )
    data_location = models.CharField(max_length=128, help_text="e.g., table number", blank=True)
    effect_description = models.TextField(
        blank=True,
        verbose_name="Effect estimate description",
        help_text="Description of the effect estimate with units, including the comparison being made (e.g., beta for IQR increase, OR for Q2 vs Q1)",
    )
    statistical_method = models.TextField(
        blank=True,
        help_text="Briefly describe the statistical analysis method (e.g., logistic regression).",
    )
    adverse_direction = models.CharField(
        max_length=12,
        choices=constants.AdverseDirection,
        default=constants.AdverseDirection.UNSPECIFIED,
        verbose_name="Adverse direction",
        help_text=" Select the direction of effect that would be adverse if observed. This does not mean that the actual results were adverse or were in that direction; this is a guide for interpretation of the results. For example, for a given neuropsychological score, is an increase interpreted as a better or worse score? For some outcomes (e.g., thyroid hormones), an association in either direction could conceivably be adverse.",
    )
    comments = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    TEXT_CLEANUP_FIELDS = (
        "sub_population",
        "outcome_measurement_timing",
        "effect_estimate_type",
        "units",
        "p_value",
        "group",
        "exposure_transform",
        "outcome_transform",
        "confidence",
        "data_location",
        "adverse_direction",
    )

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

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

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
