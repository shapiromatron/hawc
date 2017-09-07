#!/usr/bin/env python
# -*- coding: utf8 -*-
import itertools
import json
import math
from operator import xor

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

from reversion import revisions as reversion
from scipy.stats import t

from assessment.models import Assessment, BaseEndpoint
from study.models import Study
from utils.models import get_crumbs, get_distinct_charfield_opts
from utils.helper import SerializerHelper, HAWCDjangoJSONEncoder

from . import managers


class Criteria(models.Model):
    objects = managers.CriteriaManager()

    assessment = models.ForeignKey(
        'assessment.Assessment')
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    COPY_NAME = "criterias"

    class Meta:
        ordering = ('description', )
        unique_together = ('assessment', 'description')
        verbose_name_plural = "Criteria"

    def __str__(self):
        return self.description

    def copy_across_assessments(self, cw):
        new_obj, _ = self._meta.model.objects.get_or_create(
            assessment_id=cw[Assessment.COPY_NAME][self.assessment_id],
            description=self.description)
        cw[self.COPY_NAME][self.id] = new_obj.id


class Country(models.Model):
    objects = managers.CountryManager()

    code = models.CharField(
        blank=True,
        max_length=2)
    name = models.CharField(
        unique=True,
        max_length=64)

    class Meta:
        ordering = ('name', )
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class AdjustmentFactor(models.Model):
    objects = managers.AdjustmentFactorManager()
    
    assessment = models.ForeignKey(
        'assessment.Assessment')
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    COPY_NAME = "factors"

    class Meta:
        unique_together = ('assessment', 'description')
        ordering = ('description', )

    def __str__(self):
        return self.description

    def copy_across_assessments(self, cw):
        new_obj, _ = self._meta.model.objects.get_or_create(
            assessment_id=cw[Assessment.COPY_NAME][self.assessment_id],
            description=self.description)
        cw[self.COPY_NAME][self.id] = new_obj.id


class Ethnicity(models.Model):
    objects = managers.EthnicityManger()

    name = models.CharField(
        max_length=64,
        unique=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = "Ethnicities"

    def __str__(self):
        return self.name


class StudyPopulationCriteria(models.Model):
    objects = managers.StudyPopulationCriteriaManager()

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

    COPY_NAME = "spcriterias"

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.criteria_id = cw[Criteria.COPY_NAME][self.criteria_id]
        self.study_population_id = cw[StudyPopulation.COPY_NAME][self.study_population_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


class StudyPopulation(models.Model):
    objects = managers.StudyPopulationManager()

    DESIGN_CHOICES = (
        ('CO', 'Cohort'),
        ('CX', 'Cohort (Retrospective)'),
        ('CY', 'Cohort (Prospective)'),
        ('CC', 'Case-control'),
        ('NC', 'Nested case-control'),
        ('CR', 'Case report'),
        ('SE', 'Case series'),
        ('RT', 'Randomized controlled trial'),
        ('NT', 'Non-randomized controlled trial'),
        ('CS', 'Cross-sectional'),
    )

    OUTCOME_GROUP_DESIGNS = ("CC", "NC")

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

    COPY_NAME = "study_populations"

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
            return '|'.join([
                d['description'] for d in
                [d for d in lst if d['criteria_type'] == filt]
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

    def __str__(self):
        return self.name

    def get_crumbs(self):
        return get_crumbs(self, self.study)

    def can_create_sets(self):
        return self.design not in self.OUTCOME_GROUP_DESIGNS

    def copy_across_assessments(self, cw):
        children = list(itertools.chain(
            self.criteria.all(),
            self.spcriteria.all(),
            self.exposures.all(),
            self.comparison_sets.all(),
            self.outcomes.all()))
        old_id = self.id
        self.id = None
        self.study_id = cw[Study.COPY_NAME][self.study_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)


class Outcome(BaseEndpoint):
    objects = managers.OutcomeManager()

    TEXT_CLEANUP_FIELDS = (
        'name',
        'system',
        'effect',
        'effect_subtype',
    )

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
    effect_subtype = models.CharField(
        max_length=128,
        blank=True,
        help_text="Effect subtype, using common-vocabulary")
    diagnostic = models.PositiveSmallIntegerField(
        choices=DIAGNOSTIC_CHOICES)
    diagnostic_description = models.TextField()
    outcome_n = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Outcome N")
    age_of_measurement = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Age at outcome measurement",
        help_text='Textual age description when outcomes were measured '
                  '[examples include:  specific age indicated in the study '
                  '(e.g., "3 years of age, 10-12 years of age") OR standard '
                  'age categories: "infancy (1-12 months), toddler (1-2 years)'
                  ', middle childhood (6-11 years, early adolescence (12-18 '
                  'years), late adolescence (19-21 years), adulthood (>21), '
                  'older adulthood (varies)" - based on NICHD Integrated '
                  'pediatric terminology]')
    summary = models.TextField(
        blank=True,
        help_text='Summarize main findings of outcome, or describe why no '
                  'details are presented (for example, "no association '
                  '(data not shown)")')

    COPY_NAME = "outcomes"

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @staticmethod
    def get_qs_json(queryset, json_encode=True):
        outcomes = [outcome.get_json(json_encode=False) for outcome in queryset]
        if json_encode:
            return json.dumps(outcomes, cls=HAWCDjangoJSONEncoder)
        else:
            return outcomes

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
            "outcome-effect_subtype",
            "outcome-diagnostic",
            "outcome-diagnostic_description",
            "outcome-age_of_measurement",
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
            '|'.join([str(d['name']) for d in ser['effects']]),
            ser['system'],
            ser['effect'],
            ser['effect_subtype'],
            ser['diagnostic'],
            ser['diagnostic_description'],
            ser['age_of_measurement'],
            ser['outcome_n'],
            ser['summary'],
            ser['created'],
            ser['last_updated'],
        )

    def copy_across_assessments(self, cw):
        children = list(itertools.chain(
            self.comparison_sets.all(),
            self.results.all()))

        old_id = self.id
        new_assessment_id = cw[Assessment.COPY_NAME][self.assessment_id]

        # copy base endpoint
        base = self.baseendpoint_ptr
        base.id = None
        base.assessment_id = new_assessment_id
        base.save()

        # copy outcome
        self.id = None
        self.baseendpoint_ptr = base
        self.assessment_id = new_assessment_id
        self.study_population_id = cw[StudyPopulation.COPY_NAME][self.study_population_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id

        # copy tags
        for tag in self.effects.through.objects.filter(baseendpoint_id=old_id):
            tag.id = None
            tag.baseendpoint_id = self.id
            tag.save()

        # copy other children
        for child in children:
            child.copy_across_assessments(cw)


class ComparisonSet(models.Model):
    objects = managers.ComparisonSetManager()

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

    COPY_NAME = "comparison_sets"

    class Meta:
        ordering = ('name', )

    def save(self, *args, **kwargs):
        if not xor(self.outcome is None, self.study_population is None):
            raise ValueError("An outcome or study-population is required.")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('epi:cs_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        if self.outcome:
            return self.outcome.get_assessment()
        else:
            return self.study_population.get_assessment()

    def __str__(self):
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

    def copy_across_assessments(self, cw):
        children = list(self.groups.all())
        old_id = self.id
        self.id = None
        if self.study_population_id:
            self.study_population_id = cw[StudyPopulation.COPY_NAME][self.study_population_id]
        if self.outcome_id:
            self.outcome_id = cw[Outcome.COPY_NAME][self.outcome_id]
        if self.exposure_id:
            self.exposure_id = cw[Exposure.COPY_NAME][self.exposure_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)


class Group(models.Model):
    objects = managers.GroupManager()

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

    COPY_NAME = "groups"

    class Meta:
        ordering = ('comparison_set', 'group_id', )

    def get_absolute_url(self):
        return reverse('epi:g_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.comparison_set.get_assessment()

    def __str__(self):
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
            "|".join([d["name"] for d in ser['ethnicities']]),
            ser['eligible_n'],
            ser['invited_n'],
            ser['participant_n'],
            ser['isControl'],
            ser['comments'],
            ser['created'],
            ser['last_updated'],
        )

    def copy_across_assessments(self, cw):
        children = list(self.descriptions.all())
        old_id = self.id
        self.id = None
        self.comparison_set_id = cw[ComparisonSet.COPY_NAME][self.comparison_set_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)


class Exposure(models.Model):
    objects = managers.ExposureManager()

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
        (2, "SE"),
        (3, "SEM"),
        (4, "GSD"),
        (5, "other"))

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
    age_of_exposure = models.CharField(
        max_length=32,
        blank=True,
        help_text='Textual age description for when exposure measurement '
                  'sample was taken, treatment given, or age for which survey '
                  'data apply [examples include:  specific age indicated in '
                  'the study (e.g., "gestational week 20, 3 years of age, '
                  '10-12 years of age, previous 12 months") OR standard age '
                  'categories: "fetal (in utero), neonatal (0-27 days), '
                  'infancy (1-12 months) toddler (1-2 years), middle '
                  'childhood (6-11 years, early adolescence (12-18 years),'
                  'late adolescence (19-21 years), adulthood (>21),'
                  'older adulthood (varies)" – based on NICHD Integrated'
                  'pediatric terminology]')
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
    n = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Individuals where outcome was measured")
    estimate = models.FloatField(
        blank=True,
        null=True,
        help_text="Central tendency estimate")
    estimate_type = models.PositiveSmallIntegerField(
        choices=ESTIMATE_TYPE_CHOICES,
        verbose_name="Central estimate type",
        default=0)
    variance = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Variance',
        help_text="Variance estimate")
    variance_type = models.PositiveSmallIntegerField(
        choices=VARIANCE_TYPE_CHOICES,
        default=0)
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
    lower_range = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Lower range',
        help_text='Numerical value for lower range')
    upper_range = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Upper range',
        help_text='Numerical value for upper range')
    description = models.TextField(
        blank=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    COPY_NAME = "exposures"

    class Meta:
        ordering = ('name', )
        verbose_name = "Exposure"
        verbose_name_plural = "Exposures"

    def __str__(self):
        return self.name

    @property
    def lower_bound_interval(self):
        return self.lower_range \
            if self.lower_ci is None \
            else self.lower_ci

    @property
    def upper_bound_interval(self):
        return self.upper_range \
            if self.upper_ci is None \
            else self.upper_ci

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
            "exposure-age_of_exposure",
            "exposure-duration",
            "exposure-n",
            "exposure-estimate",
            "exposure-estimate_type",
            "exposure-variance",
            "exposure-variance_type",
            "exposure-lower_ci",
            "exposure-upper_ci",
            "exposure-lower_range",
            "exposure-upper_range",
            "exposure-lower_bound_interval",
            "exposure-upper_bound_interval",
            "exposure-exposure_distribution",
            "exposure-description",
            "exposure-created",
            "exposure-last_updated",
        )

    @staticmethod
    def flat_complete_data_row(ser):
        if ser is None:
            ser = {}
        units = ser.get("metric_units", {})
        return (
            ser.get("id"),
            ser.get("url"),
            ser.get("name"),
            ser.get("inhalation"),
            ser.get("dermal"),
            ser.get("oral"),
            ser.get("in_utero"),
            ser.get("iv"),
            ser.get("unknown_route"),
            ser.get("measured"),
            ser.get("metric"),
            units.get("id"),
            units.get("name"),
            ser.get("metric_description"),
            ser.get("analytical_method"),
            ser.get("sampling_period"),
            ser.get("age_of_exposure"),
            ser.get("duration"),
            ser.get("n"),
            ser.get("estimate"),
            ser.get("estimate_type"),
            ser.get("variance"),
            ser.get("variance_type"),
            ser.get("lower_ci"),
            ser.get("upper_ci"),
            ser.get("lower_range"),
            ser.get("upper_range"),
            ser.get("lower_bound_interval"),
            ser.get("upper_bound_interval"),
            ser.get("exposure_distribution"),
            ser.get("description"),
            ser.get("created"),
            ser.get("last_updated"),
        )

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.study_population_id = cw[StudyPopulation.COPY_NAME][self.study_population_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


class GroupNumericalDescriptions(models.Model):
    objects = managers.GroupNumericalDescriptionsManager()

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

    COPY_NAME = "group_descriptions"

    def __str__(self):
        return self.description

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.group_id = cw[Group.COPY_NAME][self.group_id]
        self.save()
        cw[GroupNumericalDescriptions.COPY_NAME][old_id] = self.id


class ResultMetric(models.Model):
    objects = managers.ResultMetricManager()

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

    def __str__(self):
        return self.metric


class ResultAdjustmentFactor(models.Model):
    objects = managers.ResultAdjustmentFactorManager()

    adjustment_factor = models.ForeignKey('AdjustmentFactor',
        related_name='resfactors')
    result = models.ForeignKey('Result',
        related_name='resfactors')
    included_in_final_model = models.BooleanField(default=True)

    COPY_NAME = "rfactors"

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.adjustment_factor_id = cw[AdjustmentFactor.COPY_NAME][self.adjustment_factor_id]
        self.result_id = cw[Result.COPY_NAME][self.result_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


class Result(models.Model):
    objects = managers.ResultManager()

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
        (2, "SE"),
        (3, "SEM"),
        (4, "GSD"),
        (5, "other"))

    name = models.CharField(
        max_length=256)
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
    statistical_test_results = models.TextField(
        blank=True)
    trend_test = models.CharField(
        verbose_name="Trend test result",
        max_length=128,
        blank=True,
        help_text="Enter result, if available (ex: p=0.015, p≤0.05, n.s., etc.)")
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

    COPY_NAME = "results"

    @property
    def factors_applied(self):
        return self.adjustment_factors\
            .filter(resfactors__included_in_final_model=True)

    @property
    def factors_considered(self):
        return self.adjustment_factors\
            .filter(resfactors__included_in_final_model=False)

    def __str__(self):
        return self.name

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
            "result-name",
            "result-metric_description",
            "result-data_location",
            "result-population_description",
            "result-dose_response",
            "result-dose_response_details",
            "result-prevalence_incidence",
            "result-statistical_power",
            "result-statistical_power_details",
            "result-statistical_test_results",
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
            return '|'.join([
                d['description'] for d in
                [d for d in lst if d['included_in_final_model'] == isIncluded]
            ])

        return (
            ser['metric']['id'],
            ser['metric']['metric'],
            ser['metric']['abbreviation'],
            ser['id'],
            ser['name'],
            ser['metric_description'],
            ser['data_location'],
            ser['population_description'],
            ser['dose_response'],
            ser['dose_response_details'],
            ser['prevalence_incidence'],
            ser['statistical_power'],
            ser['statistical_power_details'],
            ser['statistical_test_results'],
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

    def copy_across_assessments(self, cw):
        children = list(itertools.chain(
            self.adjustment_factors.all(),
            self.resfactors.all(),
            self.results.all()))
        old_id = self.id
        self.id = None
        self.outcome_id = cw[Outcome.COPY_NAME][self.outcome_id]
        self.comparison_set_id = cw[ComparisonSet.COPY_NAME][self.comparison_set_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)


class GroupResult(models.Model):
    objects = managers.GroupResultManager()

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
    lower_range = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Lower range',
        help_text='Numerical value for lower range')
    upper_range = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Upper range',
        help_text='Numerical value for upper range')
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

    COPY_NAME = "groupresults"

    class Meta:
        ordering = ('result', 'group__group_id')

    @property
    def p_value_text(self):
        txt = self.get_p_value_qualifier_display()
        if self.p_value is not None:
            if txt in ["=", "-", "n.s."]:
                txt = "{0:g}".format(self.p_value)
            else:
                txt = "{0}{1:g}".format(txt, self.p_value)

        return txt

    @property
    def lower_bound_interval(self):
        return self.lower_range \
            if self.lower_ci is None \
            else self.lower_ci

    @property
    def upper_bound_interval(self):
        return self.upper_range \
            if self.upper_ci is None \
            else self.upper_ci

    @staticmethod
    def flat_complete_header_row():
        return (
            "result_group-id",
            "result_group-n",
            "result_group-estimate",
            "result_group-variance",
            "result_group-lower_ci",
            "result_group-upper_ci",
            "result_group-lower_range",
            "result_group-upper_range",
            "result_group-lower_bound_interval",
            "result_group-upper_bound_interval",
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
            ser["lower_range"],
            ser["upper_range"],
            ser["lower_bound_interval"],
            ser["upper_bound_interval"],
            ser["p_value_qualifier"],
            ser["p_value"],
            ser["is_main_finding"],
            ser["main_finding_support"],
            ser["created"],
            ser["last_updated"],
        )

    @staticmethod
    def stdev(variance_type, variance, n):
        # calculate stdev given re
        if variance_type == 'SD':
            return variance
        elif variance_type in ['SE', 'SEM'] and variance is not None and n is not None:
            return variance * math.sqrt(n)
        else:
            return None

    @classmethod
    def getStdevs(cls, variance_type, rgs):
        for rg in rgs:
            rg['stdev'] = cls.stdev(variance_type, rg['variance'], rg['n'])

    @staticmethod
    def getConfidenceIntervals(variance_type, groups):
        """
        Expects a dictionary of endpoint groups and the endpoint variance-type.
        Appends results to the dictionary for each endpoint-group.

        Confidence interval calculated using a two-tailed t-test,
        assuming 95% confidence interval.
        """

        for grp in groups:
            lower_ci = grp.get('lower_ci')
            upper_ci = grp.get('upper_ci')
            n = grp.get('n')
            if (
                    lower_ci is None and
                    upper_ci is None and
                    n is not None and
                    grp['lower_range'] is None and
                    grp['upper_range'] is None and
                    grp['estimate'] is not None and
                    grp['variance'] is not None
               ):
                    est = grp['estimate']
                    var = grp['variance']
                    z = t.ppf(0.975, max(n-1, 1))
                    change = None

                    if variance_type == 'SD':
                        change = z * var / math.sqrt(n)
                    elif variance_type in ('SE', 'SEM'):
                        change = z * var

                    if change is not None:
                        lower_ci = round(est - change, 2)
                        upper_ci = round(est + change, 2)

                    grp.update(lower_ci=lower_ci, upper_ci=upper_ci, ci_calc=True)

    @staticmethod
    def percentControl(estimate_type, variance_type, rgs):
        """
        Expects a dictionary of result groups, the result estimate_type, and
        result variance_type. Appends results to the dictionary for each result-group.

        Calculates a 95% confidence interval for the percent-difference from
        control, taking into account variance from both groups using a
        Fisher Information Matrix, assuming independent normal distributions.

        Only calculates if estimate_type is 'median' or 'mean' and variance_type
        is 'SD', 'SE', or 'SEM', all cases are true with a normal distribution.
        """
        def get_control_group(rgs):
            """
            - If 0 groups are control=true, the first group will be chosen as control
            - If 1 group is control=true, it will be used as control
            - If ≥2 groups is control=true, a random control group will be chosen as control
            """
            control = None

            for i, rg in enumerate(rgs):
                if rg['group']['isControl']:
                    control = rg
                    break

            if control is None:
                control = rgs[0]

            return control['n'], control['estimate'], control.get('stdev')

        if len(rgs) == 0:
            return

        n_1, mu_1, sd_1 = get_control_group(rgs)

        for i, rg in enumerate(rgs):

            mean = low = high = None

            if estimate_type in ['median', 'mean'] and \
               variance_type in ['SD', 'SE', 'SEM']:

                n_2 = rg['n']
                mu_2 = rg['estimate']
                sd_2 = rg.get('stdev')

                if mu_1 and mu_2 and mu_1 != 0:
                    mean = (mu_2 - mu_1) / mu_1 * 100.
                    if sd_1 and sd_2 and n_1 and n_2:
                        sd = math.sqrt(
                            pow(mu_1, -2) * (
                                (pow(sd_2, 2) / n_2) +
                                (pow(mu_2, 2) * pow(sd_1, 2)) /
                                (n_1 * pow(mu_1, 2))
                            )
                        )
                        ci = (1.96 * sd) * 100
                        rng = sorted([mean - ci, mean + ci])
                        low = rng[0]
                        high = rng[1]

            rg.update(
                percentControlMean=mean,
                percentControlLow=low,
                percentControlHigh=high
            )

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.result_id = cw[Result.COPY_NAME][self.result_id]
        self.group_id = cw[Group.COPY_NAME][self.group_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id


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
