#!/usr/bin/env python
# -*- coding: utf8 -*-
from operator import xor

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

from assessment.models import BaseEndpoint
from utils.models import get_crumbs


class Criteria(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment')
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('description', )
        unique_together = ('assessment', 'description')
        verbose_name_plural = "Criteria"

    def __unicode__(self):
        return self.description


class Country(models.Model):
    code = models.CharField(
        unique=True,
        max_length=2)
    name = models.CharField(
        unique=True,
        max_length=64)

    class Meta:
        ordering = ('name', )
        verbose_name_plural = "Countries"

    def __unicode__(self):
        return self.name


class AdjustmentFactor(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment')
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        unique_together = ('assessment', 'description')
        ordering = ('description', )

    def __unicode__(self):
        return self.description


class Ethnicity(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "Ethnicities"

    def __unicode__(self):
        return self.name


class StudyPopulationCriteria(models.Model):
    CRITERIA_TYPE = (
        ("I", "Inclusion"),
        ("E", "Exclusion"),
        ("C", "Confounding")
    )
    criteria = models.ForeignKey('Criteria',
        related_name='spcriteria')
    study_population = models.ForeignKey('StudyPopulation',
        related_name='spcriteria')
    criteria_type = models.CharField(
        max_length=1,
        choices=CRITERIA_TYPE)


class StudyPopulation(models.Model):

    DESIGN_CHOICES = (
        ('CC', 'Case control'),
        ('NC', 'Nested case control'),
        ('CR', 'Case report'),
        ('SE', 'Case series'),
        ('CT', 'Controlled trial'),
        ('CS', 'Cross sectional'),
    )

    study = models.ForeignKey(
        'study.Study',
        related_name="study_populations2")
    name = models.CharField(
        max_length=256)
    design = models.CharField(
        max_length=2,
        choices=DESIGN_CHOICES)
    country = models.ForeignKey(
        Country)
    region = models.CharField(
        max_length=128,
        blank=True)
    state = models.CharField(
        max_length=128,
        blank=True)
    eligible_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Eligible N")
    invited_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Invited N")
    participant_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Participant N")
    criteria = models.ManyToManyField(
        Criteria,
        through=StudyPopulationCriteria,
        related_name='populations')
    comments = models.TextField(
        blank=True,
        help_text="Note matching criteria, etc."
    )
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('name', )

    def get_absolute_url(self):
        return reverse('epi2:sp_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.study.get_assessment()

    @property
    def inclusion_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="I")

    @property
    def exclusion_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="E")

    @property
    def confounding_criteria(self):
        return self.criteria.filter(spcriteria__criteria_type="C")

    def __unicode__(self):
        return self.name

    def get_crumbs(self):
        return get_crumbs(self, self.study)

    def can_create_groups(self):
        return self.design not in ("CC", "NC")


class Outcome(BaseEndpoint):

    DIAGNOSTIC_CHOICES = (
        (0, 'not reported'),
        (1, 'medical professional or test'),
        (2, 'medical records'),
        (3, 'self-reported'))

    study_population = models.ForeignKey(
        StudyPopulation,
        related_name='outcomes')
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
                  "(ex: Figure 1, Table 2, etc.)")  # TODO: move this to results
    population_description = models.CharField(
        max_length=128,
        help_text='Detailed description of the population being studied for this outcome, '
                  'which may be a subset of the entire study-population. For example, '
                  '"US (national) NHANES 2003-2008, Hispanic children 6-18 years, ♂♀ (n=797)"',
        blank=True)
    diagnostic = models.PositiveSmallIntegerField(
        choices=DIAGNOSTIC_CHOICES)
    diagnostic_description = models.TextField()
    outcome_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Outcome N")
    summary = models.TextField(
        blank=True,
        help_text='Summarize main findings of outcome, or describe why no '
                  'details are presented (for example, "no association '
                  '(data not shown)")')
    prevalence_incidence = models.TextField(
        blank=True)

    def get_absolute_url(self):
        return reverse('epi2:outcome_detail', kwargs={'pk': self.pk})

    def get_crumbs(self):
        return get_crumbs(self, self.study_population)

    def can_create_groups(self):
            return not self.study_population.can_create_groups()


class GroupCollection(models.Model):
    """
    A collection of comparable groups of individuals.
    """
    study_population = models.ForeignKey(
        StudyPopulation,
        related_name='group_collections',
        null=True)
    outcome = models.ForeignKey(
        Outcome,
        related_name='group_collections',
        null=True)
    name = models.CharField(
        max_length=256)
    exposure = models.ForeignKey(
        "Exposure2",
        related_name="groups",
        help_text="Exposure-group associated with this group",
        blank=True,
        null=True)
    description = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('name', )

    def save(self, *args, **kwargs):
        if not xor(self.outcome is None, self.study_population is None):
            raise ValueError("An outcome or study-population is required.")
        super(GroupCollection, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('epi2:gc_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        if self.outcome:
            return self.outcome.get_assessment()
        else:
            return self.study_population.get_assessment()

    def __unicode__(self):
        return self.name

    def get_crumbs(self):
        if self.outcome:
            return get_crumbs(self, self.outcome)
        else:
            return get_crumbs(self, self.study_population)


class Group(models.Model):
    """
    A collection of individuals.
    """
    SEX_CHOICES = (
        ("U", "Not reported"),
        ("M", "Male"),
        ("F", "Female"),
        ("B", "Male and Female"))

    IS_CONTROL_CHOICES = (
        (True, "Yes"),
        (False, "No"),
        (None, "N/A"),
    )

    collection = models.ForeignKey(
        GroupCollection,
        related_name="groups")
    group_id = models.PositiveSmallIntegerField()
    name = models.CharField(
        max_length=256)
    numeric = models.FloatField(
        verbose_name='Numerical value (sorting)',
        help_text='Numerical value, can be used for sorting',
        blank=True,
        null=True)
    comparative_name = models.CharField(
        max_length=64,
        verbose_name="Comparative Name",
        help_text='Group and value, displayed in plots, for example '
                  '"1.5-2.5(Q2) vs ≤1.5(Q1)", or if only one group is available, '
                  '"4.8±0.2 (mean±SEM)"',
        blank=True)
    sex = models.CharField(
        max_length=1,
        default="U",
        choices=SEX_CHOICES)
    ethnicities = models.ManyToManyField(
        Ethnicity,
        blank=True)
    eligible_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Eligible N")
    invited_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Invited N")
    participant_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Participant N")
    fraction_male = models.FloatField(
        blank=True,
        null=True,
        help_text="Expects a value between 0 and 1, inclusive (leave blank if unknown)",
        validators=[MinValueValidator(0), MaxValueValidator(1)])
    fraction_male_calculated = models.BooleanField(
        default=False,
        help_text="Was the fraction-male value calculated/estimated from literature?")
    isControl = models.NullBooleanField(
        verbose_name="Control?",
        default=None,
        choices=IS_CONTROL_CHOICES,
        help_text="Should this group be interpreted as a null/control group")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('collection', 'group_id', )

    def get_absolute_url(self):
        return reverse('epi2:g_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.collection.get_assessment()

    def __unicode__(self):
        return self.name

    def get_crumbs(self):
        return get_crumbs(self, self.collection)


class Exposure2(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation,
        related_name='exposures')
    name = models.CharField(
        max_length=128,
        help_text='Name of exposure-route')
    inhalation = models.BooleanField(
        default=False)
    dermal = models.BooleanField(
        default=False)
    oral = models.BooleanField(
        default=False)
    in_utero = models.BooleanField(
        default=False)
    iv = models.BooleanField(
        default=False,
        verbose_name="Intravenous (IV)")
    unknown_route = models.BooleanField(
        default=False)
    metric = models.TextField(
        verbose_name="Measurement Metric")
    metric_units = models.ForeignKey(
        'assessment.DoseUnits')
    metric_description = models.TextField(
        verbose_name="Measurement Description")
    analytical_method = models.TextField(
        help_text="Include details on the lab-techniques for exposure "
                  "measurement in samples.")
    sampling_period = models.CharField(
        max_length=128,
        help_text='Exposure sampling period')
    duration = models.CharField(
        max_length=128,
        blank=True,
        help_text='Exposure duration')
    exposure_distribution = models.CharField(
        max_length=128,
        blank=True,
        help_text='May be used to describe the exposure distribution, for '
                  'example, "2.05 µg/g creatinine (urine), geometric mean; '
                  '25th percentile = 1.18, 75th percentile = 3.33"')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)
    control_description = models.TextField(
        blank=True)

    class Meta:
        ordering = ('name', )
        verbose_name = "Exposure"
        verbose_name_plural = "Exposures"

    def __unicode__(self):
        return self.name

    def get_assessment(self):
        return self.study_population.get_assessment()

    def get_absolute_url(self):
        return reverse('epi2:exp_detail', kwargs={'pk': self.pk})

    def get_crumbs(self):
        return get_crumbs(self, self.study_population)


class GroupNumericalDescriptions(models.Model):

    MEAN_TYPE_CHOICES = (
        (0, None),
        (1, "mean"),
        (2, "geometric mean"),
        (3, "median"),
        (3, "other"))

    VARIANCE_TYPE_CHOICES = (
        (0, None),
        (1, "SD"),
        (2, "SEM"),
        (3, "GSD"),
        (4, "other"))

    LOWER_LIMIT_CHOICES = (
        (0, None),
        (1, 'lower limit'),
        (2, '5% CI'),
        (3, 'other'))

    UPPER_LIMIT_CHOICES = (
        (0, None),
        (1, 'upper limit'),
        (2, '95% CI'),
        (3, 'other'))

    group = models.ForeignKey(
        Group,
        related_name="descriptions")
    description = models.CharField(
        max_length=128,
        help_text="Description if numeric ages do not make sense for this "
                  "study-population (ex: longitudinal studies)")
    mean = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Central estimate')
    mean_type = models.PositiveSmallIntegerField(
        choices=MEAN_TYPE_CHOICES,
        verbose_name="Central estimate type",
        default=0)
    is_calculated = models.BooleanField(
        default=False,
        help_text="Was value calculated/estimated from literature?")
    variance = models.FloatField(
        blank=True,
        null=True)
    variance_type = models.PositiveSmallIntegerField(
        choices=VARIANCE_TYPE_CHOICES,
        default=0)
    lower = models.FloatField(
        blank=True,
        null=True)
    lower_type = models.PositiveSmallIntegerField(
        choices=LOWER_LIMIT_CHOICES,
        default=0)
    upper = models.FloatField(
        blank=True,
        null=True)
    upper_type = models.PositiveSmallIntegerField(
        choices=UPPER_LIMIT_CHOICES,
        default=0)

    def __unicode__(self):
        return self.description


class ResultMetric(models.Model):
    metric = models.CharField(
        max_length=128,
        unique=True)
    abbreviation = models.CharField(
        max_length=32)
    isLog = models.BooleanField(
        default=True,
        verbose_name="Display as log",
        help_text="When plotting, use a log base 10 scale")
    showForestPlot = models.BooleanField(
        default=True,
        verbose_name="Show on forest plot",
        help_text="Does forest-plot representation of result make sense?")
    reference_value = models.FloatField(
        help_text="Null hypothesis value for reference, if applicable",
        default=1,
        blank=True,
        null=True)
    order = models.PositiveSmallIntegerField(
        help_text="Order as they appear in option-list")

    class Meta:
        ordering = ('order', )

    def __unicode__(self):
        return self.metric


class ResultAdjustmentFactor(models.Model):
    adjustment_factor = models.ForeignKey('AdjustmentFactor',
        related_name='resfactors')
    result = models.ForeignKey('Result',
        related_name='resfactors')
    included_in_final_model = models.BooleanField(default=True)


class Result(models.Model):

    DOSE_RESPONSE_CHOICES = (
        (0, "not-applicable"),
        (1, "monotonic"),
        (2, "non-monotonic"),
        (3, "no trend"),
        (4, "not reported"))

    STATISTICAL_POWER_CHOICES = (
        (0, 'not reported or calculated'),
        (1, 'appears to be adequately powered (sample size met)'),
        (2, 'somewhat underpowered (sample size is 75% to <100% of recommended)'),
        (3, 'underpowered (sample size is 50 to <75% required)'),
        (4, 'severely underpowered (sample size is <50% required)'))

    outcome = models.ForeignKey(
        Outcome,
        related_name="results")
    groups = models.ForeignKey(
        GroupCollection,
        related_name="results")
    metric = models.ForeignKey(
        ResultMetric,
        related_name="results",
        help_text="&nbsp;")
    metric_description = models.TextField(
        blank=True,
        help_text="Add additional text describing the metric used, if needed.")
    adjustment_factors = models.ManyToManyField(
        AdjustmentFactor,
        through=ResultAdjustmentFactor,
        related_name='outcomes',
        blank=True)
    dose_response = models.PositiveSmallIntegerField(
        verbose_name="Dose Response Trend",
        help_text="Was a trend observed?",
        default=0,
        choices=DOSE_RESPONSE_CHOICES)
    dose_response_details = models.TextField(
        blank=True)
    statistical_power = models.PositiveSmallIntegerField(
        help_text="Is the study sufficiently powered?",
        default=0,
        choices=STATISTICAL_POWER_CHOICES)
    statistical_power_details = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    @property
    def factors_applied(self):
        return self.adjustment_factors.filter(resfactors__included_in_final_model=True)

    @property
    def factors_considered(self):
        return self.adjustment_factors.filter(resfactors__included_in_final_model=False)

    def __unicode__(self):
        return u"{0}: {1}".format(self.groups, self.metric)

    def get_assessment(self):
        return self.outcome.get_assessment()

    def get_absolute_url(self):
        return reverse('epi2:result_detail', kwargs={'pk': self.pk})

    def get_crumbs(self):
        return get_crumbs(self, self.outcome)


class GroupResult(models.Model):

    P_VALUE_QUALIFIER_CHOICES = (
        ('-', 'n.s.'),
        ('<', '<'),
        ('=', '='))

    MAIN_FINDING_CHOICES = (
        (3, "not-reported"),
        (2, "supportive"),
        (1, "inconclusive"),
        (0, "not-supportive"))

    measurement = models.ForeignKey(
        Result,
        related_name="results")
    group = models.ForeignKey(
        Group,
        related_name="results")
    n = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Individuals in group where outcome was measured")
    estimate = models.FloatField(
        blank=True,
        null=True,
        help_text="Central tendency estimate for group")
    se = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Standard Error (SE)',
        help_text="Standard error estimate for group")
    lower_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Lower CI',
        help_text="Numerical value for lower-confidence interval")
    upper_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Upper CI',
        help_text="Numerical value for upper-confidence interval")
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name='Confidence Interval (CI)',
        help_text='A 95% CI is written as 0.95.')
    p_value_qualifier = models.CharField(
        max_length=1,
        choices=P_VALUE_QUALIFIER_CHOICES,
        default="-",
        verbose_name='p-value qualifier')
    p_value = models.FloatField(
        blank=True,
        null=True,
        verbose_name='p-value')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)
    is_main_finding = models.BooleanField(
        blank=True,
        verbose_name="Main finding",
        help_text="Is this the main-finding for this outcome?")
    main_finding_support = models.PositiveSmallIntegerField(
        choices=MAIN_FINDING_CHOICES,
        help_text="Are the results supportive of the main-finding?",
        default=1)

    class Meta:
        ordering = ('measurement', 'group__group_id')
