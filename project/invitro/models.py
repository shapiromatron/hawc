#!/usr/bin/env python
# -*- coding: utf8 -*-
from django.core.validators import MinValueValidator
from django.db import models

import reversion

from assessment.models import BaseEndpoint
from animal.models import DoseUnits
from utils.helper import SerializerHelper
from utils.models import AssessmentRootedTagTree


class IVChemical(models.Model):
    study = models.ForeignKey(
        'study.Study',
        related_name='ivchemicals')
    name = models.CharField(
        max_length=128)
    cas = models.CharField(
        max_length=40,
        blank=True,
        verbose_name="Chemical identifier (CAS)")
    cas_inferred = models.BooleanField(
        default=False,
        verbose_name="CAS inferred?",
        help_text="Was the correct CAS inferred or incorrect in the original document?")
    cas_notes = models.CharField(
        max_length=128,
        verbose_name="CAS determination notes")
    source = models.CharField(
        max_length=128,
        verbose_name="Source of chemical")
    purity = models.CharField(
        max_length=32,
        verbose_name="Chemical purity",
        help_text="Example")
    purity_confirmed = models.BooleanField(
        default=False,
        verbose_name="Purity experimentally confirmed")
    purity_confirmed_notes = models.TextField(
        blank=True)
    dilution_storage_notes = models.TextField(
        help_text="Dilution, storage, and observations such as precipitation should be noted here.")

    def __unicode__(self):
        return self.name


class IVCellType(models.Model):

    SEX_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('mf', 'Male and female'),
        ('na', 'Not-applicable'),
        ('nr', 'Not-reported'))

    SEX_SYMBOLS = {
        'm':  u'♂',
        'f':  u'♀',
        'mf': u'♂♀',
        'na': u'N/A',
        'nr': u'N/R'}

    study = models.ForeignKey(
        'study.Study',
        related_name='ivcelltypes')
    species = models.CharField(
        max_length=64)
    sex = models.CharField(
        max_length=2,
        choices=SEX_CHOICES)
    cell_type = models.CharField(
        max_length=64)
    tissue = models.CharField(
        max_length=64)
    source = models.CharField(
        max_length=128,
        verbose_name="Source of cell cultures")

    def __unicode__(self):
        return self.cell_type

    def get_sex_symbol(self):
        return self.SEX_SYMBOLS.get(self.sex)


class IVExperiment(models.Model):

    METABOLIC_ACTIVATION_CHOICES = (
        ('+',  'with metabolic activation'),
        ('-',  'without metabolic activation'),
        ('na', 'not applicable'),
        ('nr', 'not reported'))

    study = models.ForeignKey(
        'study.Study',
        related_name='ivexperiments')
    cell_type = models.ForeignKey(
        IVCellType,
        related_name='ivexperiments')
    transfection = models.CharField(
        max_length=256,
        help_text="Details on transfection methodology and details on genes or "
                  "other genetic material introduced into assay, or \"not-applicable\"")
    cell_line = models.CharField(
        max_length=128,
        help_text="Description of type of cell-line used (ex: "
                  "primary cell-line, immortalized cell-line, stably transfected "
                  "cell-line, transient transfected cell-line, etc.)")
    dosing_notes = models.TextField(
        blank=True,
        help_text="Notes describing dosing-protocol, including duration-details")
    metabolic_activation = models.CharField(
        max_length=2,
        choices=METABOLIC_ACTIVATION_CHOICES,
        default='nr',
        help_text="Was metabolic-activation used in system (ex: S9)?")
    serum = models.CharField(
        max_length=128,
        verbose_name="Percent serum, serum-type, and/or description")
    has_positive_control = models.BooleanField(
        default=False)
    positive_control = models.CharField(
        max_length=128,
        blank=True,
        help_text="Positive control chemical or other notes")
    has_negative_control = models.BooleanField(
        default=False)
    negative_control = models.CharField(
        max_length=128,
        blank=True,
        help_text="Negative control chemical or other notes")
    has_vehicle_control = models.BooleanField(
        default=False)
    vehicle_control = models.CharField(
        max_length=128,
        blank=True,
        help_text="Vehicle control chemical or other notes")
    control_notes = models.CharField(
        max_length=128,
        blank=True,
        help_text="Additional details related to controls")
    dose_units = models.ForeignKey(
        DoseUnits,
        related_name='ivexperiments')


class IVEndpointCategory(AssessmentRootedTagTree):
    cache_template_taglist = 'invitro.ivendpointcategory.taglist.assessment-{0}'
    cache_template_tagtree = 'invitro.ivendpointcategory.tagtree.assessment-{0}'

    def __unicode__(self):
        return self.name


class IVEndpoint(BaseEndpoint):

    VARIANCE_TYPE_CHOICES = (
        (0, "NA"),
        (1, "SD"),
        (2, "SE"))

    DATA_TYPE_CHOICES = (
        ('C', 'Continuous'),
        ('D', 'Dichotomous'),
        ('NR', 'Not reported'))

    MONOTONICITY_CHOICES = (
        (0, "N/A, single dose level study"),
        (1, "N/A, no effects detected"),
        (2, "yes, visual appearance of monotonicity but no trend"),
        (3, "yes, monotonic and significant trend"),
        (4, "yes, visual appearance of non-monotonic but no trend"),
        (5, "yes, non-monotonic and significant trend"),
        (6, "no pattern"),
        (7, "unclear"),
        (8, "not-reported"))

    OVERALL_PATTERN_CHOICES = (
        (0, "not-available"),
        (1, "increase"),
        (2, "increase, then decrease"),
        (3, "decrease"),
        (4, "decrease, then increase"),
        (5, "no clear pattern"))

    TREND_TEST_RESULT_CHOICES = (
        (0, "not-reported"),
        (1, "not-analyzed"),
        (2, "not-applicable"),
        (3, "significant"),
        (4, "not-significant"))

    OBSERVATION_TIME_UNITS = (
        (0, "not-reported"),
        (1, "seconds"),
        (2, "minutes"),
        (3, "hours"),
        (4, "days"),
        (5, "weeks"),
        (6, "months"))

    experiment = models.ForeignKey(
        IVExperiment,
        related_name="experiments")
    chemical = models.ForeignKey(
        IVChemical,
        related_name="endpoints")
    category = models.ForeignKey(IVEndpointCategory,
        related_name="endpoints")
    assay_type = models.CharField(
        max_length=128)
    short_description = models.CharField(
        max_length=64,
        help_text="Short (<64 character) description of effect & measurement")
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
                  "(ex: Figure 1, Table 2, etc.)")
    data_type = models.CharField(
        max_length=2,
        choices=DATA_TYPE_CHOICES,
        default="C",
        verbose_name="Dataset type")
    variance_type = models.PositiveSmallIntegerField(
        default=0,
        choices=VARIANCE_TYPE_CHOICES)
    response_units = models.CharField(
        max_length=64,
        verbose_name="Response units")
    observation_time = models.FloatField(
        default=-999)
    observation_time_units = models.PositiveSmallIntegerField(
         default=0,
         choices=OBSERVATION_TIME_UNITS)
    NOAEL = models.SmallIntegerField(
        verbose_name="NOAEL",
        default=-999)
    LOAEL = models.SmallIntegerField(
        verbose_name="NOAEL",
        default=-999)
    monotonicity = models.PositiveSmallIntegerField(
        default=8,
        choices=MONOTONICITY_CHOICES)
    overall_pattern = models.PositiveSmallIntegerField(
        default=0,
        choices=OVERALL_PATTERN_CHOICES)
    statistical_test_notes = models.CharField(
        max_length=256,
        blank=True,
        help_text="Notes describing details on the statistical tests performed")
    trend_test = models.PositiveSmallIntegerField(
        default=0,
        choices=TREND_TEST_RESULT_CHOICES)
    endpoint_notes = models.TextField(
        blank=True,
        help_text="Any additional notes regarding the endpoint itself")
    result_notes = models.TextField(
        blank=True,
        help_text="Qualitative description of the results")
    additional_fields = models.TextField(
        default="{}")

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @classmethod
    def get_maximum_number_doses(cls, queryset):
        max_val = 0
        qs = queryset\
                .annotate(max_egs=models.Count('groups'))\
                .values_list('max_egs', flat=True)
        if len(qs)>0: max_val = max(qs)
        return max_val

    @classmethod
    def get_maximum_number_benchmarks(cls, queryset):
        max_val = 0
        qs = queryset\
                .annotate(max_benchmarks=models.Count('benchmarks'))\
                .values_list('max_benchmarks', flat=True)
        if len(qs)>0: max_val = max(qs)
        return max_val

    @classmethod
    def get_docx_template_context(cls, queryset):
        return {
            "field1": "body and mind",
            "field2": "well respected man",
            "field3": 1234,
            "nested": {"object": {"here": u"you got it!"}},
            "extra": "tests",
            "tables": [
                {
                    "title": "Tom's table",
                    "row1": 'abc',
                    "row2": 'def',
                    "row3": 123,
                    "row4": 6/7.,
                },
                {
                    "title": "Frank's table",
                    "row1": 'abc',
                    "row2": 'def',
                    "row3": 223,
                    "row4": 5/7.,
                },
                {
                    "title": "Gerry's table",
                    "row1": 'cats',
                    "row2": 'dogs',
                    "row3": 123,
                    "row4": 4/7.,
                },
            ]
        }


class IVEndpointGroup(models.Model):

    DIFFERENCE_CONTROL_CHOICES = (
        ('nc', 'no-change'),
        ('-',  'decrease'),
        ('+',  'increase'),
        ('nt', 'not-tested'),
    )

    SIGNIFICANCE_CHOICES = (
        ("nr", u"not reported"),
        ("si", u"p ≤ 0.05"),
        ("ns", u"not significant"),
        ("na", u"not applicable"),
    )

    CYTOTOXICITY_CHOICES = (
        ('nr', 'not reported'),
        ('-', 'no'),
        ('+', 'yes'),
    )

    endpoint = models.ForeignKey(
        IVEndpoint,
        related_name="groups")
    dose_group_id = models.PositiveSmallIntegerField()
    dose = models.FloatField(
        validators=[MinValueValidator(0)])
    n = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)])
    response = models.FloatField(
        blank=True,
        null=True)
    variance = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)])
    difference_control = models.CharField(
        max_length=2,
        choices=DIFFERENCE_CONTROL_CHOICES,
        default="nc")
    significant_control = models.CharField(
        max_length=2,
        default="nr",
        choices=SIGNIFICANCE_CHOICES)
    cytotoxicity_observed = models.CharField(
        max_length=2,
        default="nr",
        choices=CYTOTOXICITY_CHOICES)

    class Meta:
        ordering = ('endpoint', 'dose_group_id')


class IVBenchmark(models.Model):
    endpoint = models.ForeignKey(
        IVEndpoint,
        related_name="benchmarks")
    benchmark = models.CharField(
        max_length=32)
    value = models.FloatField(
        validators=[MinValueValidator(0)])


reversion.register(IVChemical)
reversion.register(IVCellType)
reversion.register(IVExperiment)
reversion.register(IVEndpoint)
reversion.register(IVEndpointGroup)
reversion.register(IVBenchmark)
