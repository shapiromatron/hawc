#!/usr/bin/env python
# -*- coding: utf8 -*-
from operator import xor

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import reversion

from assessment.models import BaseEndpoint
from utils.models import get_crumbs
from utils.helper import SerializerHelper


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
        blank=True,
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
    criteria = models.ForeignKey(
        'Criteria',
        related_name='spcriteria')
    study_population = models.ForeignKey(
        'StudyPopulation',
        related_name='spcriteria')
    criteria_type = models.CharField(
        max_length=1,
        choices=CRITERIA_TYPE)


class StudyPopulation(models.Model):

    DESIGN_CHOICES = (
        ('CO', 'Cohort'),
        ('CC', 'Case-control'),
        ('NC', 'Nested case-control'),
        ('CR', 'Case report'),
        ('SE', 'Case series'),
        ('CT', 'Controlled trial'),
        ('CS', 'Cross sectional'),
    )

    study = models.ForeignKey(
        'study.Study',
        related_name="study_populations")
    name = models.CharField(
        max_length=256)
    design = models.CharField(
        max_length=2,
        choices=DESIGN_CHOICES)
    age_profile = models.CharField(
        max_length=128,
        blank=True,
        help_text="Age profile of population (ex: adults, children, "
                  "pregnant women, etc.)")
    source = models.CharField(
        max_length=128,
        blank=True,
        help_text="Population source (ex: general population, environmental "
                  "exposure, occupational cohort)")
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
        help_text="Note matching criteria, etc.")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    @staticmethod
    def flat_complete_header_row():
        return (
            "sp-id",
            "sp-url",
            "sp-name",
            "sp-design",
            "sp-age_profile",
            "sp-source",
            "sp-country",
            "sp-region",
            "sp-state",
            "sp-eligible_n",
            "sp-invited_n",
            "sp-participant_n",
            "sp-inclusion_criteria",
            "sp-exclusion_criteria",
            "sp-confounding_criteria",
            "sp-comments",
            "sp-created",
            "sp-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):

        def getCriteriaList(lst, filt):
            return u'|'.join([
                d['description'] for d in
                filter(lambda (d): d['criteria_type'] == filt, lst)
            ])

        return (
            ser["id"],
            ser["url"],
            ser["name"],
            ser["design"],
            ser["age_profile"],
            ser["source"],
            ser["country"],
            ser["region"],
            ser["state"],
            ser["eligible_n"],
            ser["invited_n"],
            ser["participant_n"],
            getCriteriaList(ser['criteria'], 'Inclusion'),
            getCriteriaList(ser['criteria'], 'Exclusion'),
            getCriteriaList(ser['criteria'], 'Confounding'),
            ser["comments"],
            ser["created"],
            ser["last_updated"],
        )

    class Meta:
        ordering = ('name', )

    def get_absolute_url(self):
        return reverse('epi:sp_detail', kwargs={'pk': self.pk})

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

    def can_create_sets(self):
        return self.design not in ("CC", "NC")


class Outcome(BaseEndpoint):

    DIAGNOSTIC_CHOICES = (
        (0, 'not reported'),
        (1, 'medical professional or test'),
        (2, 'medical records'),
        (3, 'self-reported'),
        (4, 'questionnaire'),
        (5, 'hospital admission'),
        (6, 'other'),
    )

    study_population = models.ForeignKey(
        StudyPopulation,
        related_name='outcomes')
    system = models.CharField(
        max_length=128,
        blank=True,
        help_text="Relevant biological system")
    effect = models.CharField(
        max_length=128,
        blank=True,
        help_text="Effect, using common-vocabulary")
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

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    def get_absolute_url(self):
        return reverse('epi:outcome_detail', kwargs={'pk': self.pk})

    def get_crumbs(self):
        return get_crumbs(self, self.study_population)

    def can_create_sets(self):
            return not self.study_population.can_create_sets()

    @staticmethod
    def flat_complete_header_row():
        return (
            "outcome-id",
            "outcome-url",
            "outcome-name",
            "outcome-effects",
            "outcome-system",
            "outcome-effect",
            "outcome-diagnostic",
            "outcome-diagnostic_description",
            "outcome-outcome_n",
            "outcome-summary",
            "outcome-created",
            "outcome-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            '|'.join([unicode(d['name']) for d in ser['effects']]),
            ser['system'],
            ser['effect'],
            ser['diagnostic'],
            ser['diagnostic_description'],
            ser['outcome_n'],
            ser['summary'],
            ser['created'],
            ser['last_updated'],
        )


class ComparisonSet(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation,
        related_name='comparison_sets',
        null=True)
    outcome = models.ForeignKey(
        Outcome,
        related_name='comparison_sets',
        null=True)
    name = models.CharField(
        max_length=256)
    exposure = models.ForeignKey(
        "Exposure",
        related_name="comparison_sets",
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
        super(ComparisonSet, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('epi:cs_detail', kwargs={'pk': self.pk})

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

    @staticmethod
    def flat_complete_header_row():
        return (
            "cs-id",
            "cs-url",
            "cs-name",
            "cs-description",
            "cs-created",
            "cs-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["url"],
            ser["name"],
            ser["description"],
            ser["created"],
            ser["last_updated"],
        )


class Group(models.Model):
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

    comparison_set = models.ForeignKey(
        ComparisonSet,
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
                  '"1.5-2.5(Q2) vs ≤1.5(Q1)", or if only one group is '
                  'available, "4.8±0.2 (mean±SEM)"',
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
    isControl = models.NullBooleanField(
        verbose_name="Control?",
        default=None,
        choices=IS_CONTROL_CHOICES,
        help_text="Should this group be interpreted as a null/control group")
    comments = models.TextField(
        blank=True,
        help_text="Any other comments related to this group")
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('comparison_set', 'group_id', )

    def get_absolute_url(self):
        return reverse('epi:g_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.comparison_set.get_assessment()

    def __unicode__(self):
        return self.name

    def get_crumbs(self):
        return get_crumbs(self, self.comparison_set)

    @staticmethod
    def flat_complete_header_row():
        return (
            "group-id",
            "group-group_id",
            "group-name",
            "group-numeric",
            "group-comparative_name",
            "group-sex",
            "group-ethnicities",
            "group-eligible_n",
            "group-invited_n",
            "group-participant_n",
            "group-isControl",
            "group-comments",
            "group-created",
            "group-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['group_id'],
            ser['name'],
            ser['numeric'],
            ser['comparative_name'],
            ser['sex'],
            u"|".join([d["name"] for d in ser['ethnicities']]),
            ser['eligible_n'],
            ser['invited_n'],
            ser['participant_n'],
            ser['isControl'],
            ser['comments'],
            ser['created'],
            ser['last_updated'],
        )


class Exposure(models.Model):
    study_population = models.ForeignKey(
        StudyPopulation,
        related_name='exposures')
    name = models.CharField(
        max_length=128,
        help_text='Name of exposure and exposure-route')
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
    measured = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="What was measured")
    metric = models.CharField(
        max_length=128,
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
        help_text='Exposure sampling period',
        blank=True)
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
    description = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('name', )
        verbose_name = "Exposure"
        verbose_name_plural = "Exposures"

    def __unicode__(self):
        return self.name

    def get_assessment(self):
        return self.study_population.get_assessment()

    def get_absolute_url(self):
        return reverse('epi:exp_detail', kwargs={'pk': self.pk})

    def get_crumbs(self):
        return get_crumbs(self, self.study_population)

    @staticmethod
    def flat_complete_header_row():
        return (
            "exposure-id",
            "exposure-url",
            "exposure-name",
            "exposure-inhalation",
            "exposure-dermal",
            "exposure-oral",
            "exposure-in_utero",
            "exposure-iv",
            "exposure-unknown_route",
            "exposure-measured",
            "exposure-metric",
            "exposure-metric_units_id",
            "exposure-metric_units_name",
            "exposure-metric_description",
            "exposure-analytical_method",
            "exposure-sampling_period",
            "exposure-duration",
            "exposure-exposure_distribution",
            "exposure-description",
            "exposure-created",
            "exposure-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["url"],
            ser["name"],
            ser["inhalation"],
            ser["dermal"],
            ser["oral"],
            ser["in_utero"],
            ser["iv"],
            ser["unknown_route"],
            ser["measured"],
            ser["metric"],
            ser["metric_units"]["id"],
            ser["metric_units"]["name"],
            ser["metric_description"],
            ser["analytical_method"],
            ser["sampling_period"],
            ser["duration"],
            ser["exposure_distribution"],
            ser["description"],
            ser["created"],
            ser["last_updated"],
        )


class GroupNumericalDescriptions(models.Model):

    MEAN_TYPE_CHOICES = (
        (0, None),
        (1, "mean"),
        (2, "geometric mean"),
        (3, "median"),
        (4, "other"))

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

    ESTIMATE_TYPE_CHOICES = (
        (0, None),
        (1, "mean"),
        (2, "geometric mean"),
        (3, "median"),
        (5, "point"),
        (4, "other"),
    )

    VARIANCE_TYPE_CHOICES = (
        (0, None),
        (1, "SD"),
        (2, "SEM"),
        (3, "GSD"),
        (4, "other"))

    outcome = models.ForeignKey(
        Outcome,
        related_name="results")
    comparison_set = models.ForeignKey(
        ComparisonSet,
        related_name="results")
    metric = models.ForeignKey(
        ResultMetric,
        related_name="results",
        help_text="&nbsp;")
    metric_description = models.TextField(
        blank=True,
        help_text="Add additional text describing the metric used, if needed.")
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
                  "(ex: Figure 1, Table 2, etc.)")
    population_description = models.CharField(
        max_length=128,
        help_text='Detailed description of the population being studied for'
                  'this outcome, which may be a subset of the entire'
                  'study-population. For example, "US (national) NHANES'
                  '2003-2008, Hispanic children 6-18 years, ♂♀ (n=797)"',
        blank=True)
    dose_response = models.PositiveSmallIntegerField(
        verbose_name="Dose Response Trend",
        help_text="Was a trend observed?",
        default=0,
        choices=DOSE_RESPONSE_CHOICES)
    dose_response_details = models.TextField(
        blank=True)
    prevalence_incidence = models.CharField(
        max_length=128,
        verbose_name="Overall incidence prevalence",
        blank=True)
    statistical_power = models.PositiveSmallIntegerField(
        help_text="Is the study sufficiently powered?",
        default=0,
        choices=STATISTICAL_POWER_CHOICES)
    statistical_power_details = models.TextField(
        blank=True)
    trend_test = models.CharField(
        verbose_name="Trend test result",
        max_length=128,
        blank=True,
        help_text=u"Enter result, if available (ex: p=0.015, p≤0.05, n.s., etc.)")
    adjustment_factors = models.ManyToManyField(
        AdjustmentFactor,
        through=ResultAdjustmentFactor,
        related_name='outcomes',
        blank=True)
    estimate_type = models.PositiveSmallIntegerField(
        choices=ESTIMATE_TYPE_CHOICES,
        verbose_name="Central estimate type",
        default=0)
    variance_type = models.PositiveSmallIntegerField(
        choices=VARIANCE_TYPE_CHOICES,
        default=0)
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name='Confidence Interval (CI)',
        help_text='A 95% CI is written as 0.95.')
    comments = models.TextField(
        blank=True,
        help_text='Summarize main findings of outcome, or describe why no '
                  'details are presented (for example, "no association '
                  '(data not shown)")')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    @property
    def factors_applied(self):
        return self.adjustment_factors\
            .filter(resfactors__included_in_final_model=True)

    @property
    def factors_considered(self):
        return self.adjustment_factors\
            .filter(resfactors__included_in_final_model=False)

    def __unicode__(self):
        return u"{0}: {1}".format(self.comparison_set, self.metric)

    def get_assessment(self):
        return self.outcome.get_assessment()

    def get_absolute_url(self):
        return reverse('epi:result_detail', kwargs={'pk': self.pk})

    def get_crumbs(self):
        return get_crumbs(self, self.outcome)

    @staticmethod
    def flat_complete_header_row():
        return (
            "metric-id",
            "metric-name",
            "metric-abbreviation",
            "result-id",
            "result-metric_description",
            "result-data_location",
            "result-population_description",
            "result-dose_response",
            "result-dose_response_details",
            "result-prevalence_incidence",
            "result-statistical_power",
            "result-statistical_power_details",
            "result-trend_test",
            "result-adjustment_factors",
            "result-adjustment_factors_considered",
            "result-estimate_type",
            "result-variance_type",
            "result-ci_units",
            "result-comments",
            "result-created",
            "result-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):

        def getFactorList(lst, isIncluded):
            return u'|'.join([
                d['description'] for d in
                filter(lambda (d): d['included_in_final_model'] == isIncluded, lst)
            ])

        return (
            ser['metric']['id'],
            ser['metric']['metric'],
            ser['metric']['abbreviation'],
            ser['id'],
            ser['metric_description'],
            ser['data_location'],
            ser['population_description'],
            ser['dose_response'],
            ser['dose_response_details'],
            ser['prevalence_incidence'],
            ser['statistical_power'],
            ser['statistical_power_details'],
            ser['trend_test'],
            getFactorList(ser['factors'], True),
            getFactorList(ser['factors'], False),
            ser['estimate_type'],
            ser['variance_type'],
            ser['ci_units'],
            ser['comments'],
            ser['created'],
            ser['last_updated'],
        )


class GroupResult(models.Model):

    P_VALUE_QUALIFIER_CHOICES = (
        (' ', '-'),
        ('-', 'n.s.'),
        ('<', '<'),
        ('=', '='),
        ('>', '>'),
    )

    MAIN_FINDING_CHOICES = (
        (3, "not-reported"),
        (2, "supportive"),
        (1, "inconclusive"),
        (0, "not-supportive"))

    result = models.ForeignKey(
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
    variance = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Variance',
        help_text="Variance estimate for group")
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
    p_value_qualifier = models.CharField(
        max_length=1,
        choices=P_VALUE_QUALIFIER_CHOICES,
        default="-",
        verbose_name='p-value qualifier')
    p_value = models.FloatField(
        blank=True,
        null=True,
        verbose_name='p-value',
        validators=[MinValueValidator(0.), MaxValueValidator(1.)])
    is_main_finding = models.BooleanField(
        blank=True,
        verbose_name="Main finding",
        help_text="Is this the main-finding for this outcome?")
    main_finding_support = models.PositiveSmallIntegerField(
        choices=MAIN_FINDING_CHOICES,
        help_text="Are the results supportive of the main-finding?",
        default=1)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('result', 'group__comparison_set_id')

    @property
    def p_value_text(self):
        txt = self.get_p_value_qualifier_display()
        if self.p_value is not None:
            if txt in ["=", "-", "n.s."]:
                txt = u"{0:g}".format(self.p_value)
            else:
                txt = u"{0}{1:g}".format(txt, self.p_value)

        return txt

    @staticmethod
    def flat_complete_header_row():
        return (
            "result_group-id",
            "result_group-n",
            "result_group-estimate",
            "result_group-variance",
            "result_group-lower_ci",
            "result_group-upper_ci",
            "result_group-p_value_qualifier",
            "result_group-p_value",
            "result_group-is_main_finding",
            "result_group-main_finding_support",
            "result_group-created",
            "result_group-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser["id"],
            ser["n"],
            ser["estimate"],
            ser["variance"],
            ser["lower_ci"],
            ser["upper_ci"],
            ser["p_value_qualifier"],
            ser["p_value"],
            ser["is_main_finding"],
            ser["main_finding_support"],
            ser["created"],
            ser["last_updated"],
        )


@receiver(post_save, sender=StudyPopulation)
@receiver(pre_delete, sender=StudyPopulation)
@receiver(post_save, sender=ComparisonSet)
@receiver(pre_delete, sender=ComparisonSet)
@receiver(post_save, sender=Exposure)
@receiver(pre_delete, sender=Exposure)
@receiver(post_save, sender=Group)
@receiver(pre_delete, sender=Group)
@receiver(post_save, sender=Outcome)
@receiver(pre_delete, sender=Outcome)
@receiver(post_save, sender=Result)
@receiver(pre_delete, sender=Result)
@receiver(post_save, sender=GroupResult)
@receiver(pre_delete, sender=GroupResult)
def invalidate_outcome_cache(sender, instance, **kwargs):
    ids = []
    instance_type = type(instance)
    filters = {}
    if instance_type is StudyPopulation:
        filters["study_population_id"] = instance.id
    elif instance_type is ComparisonSet:
        filters["results__comparison_set_id"] = instance.id
    elif instance_type is Exposure:
        filters["results__comparison_set__exposure_id"] = instance.id
    elif instance_type is Group:
        filters["results__comparison_set__groups"] = instance.id
    elif instance_type is Outcome:
        ids = [instance.id]
    elif instance_type is Result:
        ids = [instance.outcome_id]
    elif instance_type is GroupResult:
        ids = [instance.result.outcome_id]

    if len(filters) > 0:
        ids = Outcome.objects.filter(**filters).values_list('id', flat=True)

    Outcome.delete_caches(ids)


reversion.register(Country)
reversion.register(Criteria)
reversion.register(Ethnicity)
reversion.register(StudyPopulationCriteria)
reversion.register(AdjustmentFactor)
reversion.register(ResultAdjustmentFactor)
reversion.register(StudyPopulation, follow=('country', 'spcriteria'))
reversion.register(ComparisonSet)
reversion.register(Exposure)
reversion.register(Outcome, follow=('effects',))
reversion.register(Group, follow=('ethnicities',))
reversion.register(Result, follow=('adjustment_factors', 'resfactors', 'results'))
reversion.register(GroupResult)
