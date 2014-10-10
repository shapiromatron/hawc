#!/usr/bin/env python
# -*- coding: utf8 -*-
import json
import logging

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models

from assessment.models import BaseEndpoint
from animal.models import DoseUnits, Species, Strain
from utils.helper import HAWCDjangoJSONEncoder, build_excel_file, build_tsv_file

import reversion


EFFECT_DIRECTION_CHOICES = (
    ('u', 'Up'),
    ('d', 'Down'),
    ('i', 'Inconclusive'),
    ('ui', 'Up/Inconclusive'),
    ('di', 'Down/Inconclusive'))

DIR_EFFECT_SYMBOL_CW = {
    'u':  u'↑',
    'd':  u'↓',
    'i':  u'↔',
    'ui': u'↑↔',
    'di': u'↓↔'}

RESPONSE_TREND_CHOICES = (
    ('m', 'Monotonic'),
    ('n', 'Non-monotonic'),
    ('i', 'N/A'))

SEX_SYMBOL_CW = {
    'm':  u'♂',
    'f':  u'♀',
    'b':  u'♂♀',
    'na': u'N/A',
    'nr': u'N/R'}

GENERATION_CHOICES = (
    ('f0', 'F0'),
    ('f1', 'F1'),
    ('f2', 'F2'),
    ('na', 'Not-applicable'))

DATA_TYPE_CHOICES = (
    ('C', 'Continuous'),
    ('D', 'Dichotomous'))

EVIDENCE_STREAM_CHOICES = (
    ('i', 'in vitro'),
    ('e', 'ex vivo'))


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


# class IVExperiment(models.Model):

#     SEX_CHOICES = (
#         ('m', 'Male'),
#         ('f', 'Female'),
#         ('b', 'Male and female'),
#         ('na', 'Not-applicable'),
#         ('nr', 'Not-reported'))

#     OBSERVATION_TIME_UNITS = (
#         (0, 'add'), )

#     study = models.ForeignKey(
#         'study.Study',
#         related_name='ivexperiments')
#     name = models.CharField(
#         max_length=128)
#     species = models.ForeignKey(
#         Species)
#     sex = models.CharField(
#         max_length=2,
#         choices=SEX_CHOICES)
#     cell_type = models.CharField(
#         max_length=64)
#     tissue = models.CharField(
#         max_length=64)
#     diagnosis = models.CharField(
#         max_length=64,
#         default="normal")
#     assay_category = models.CharField(
#         max_length=128)
#     source = models.CharField(
#         max_length=128,
#         verbose_name="Source of cell cultures")
#     culture = models.CharField(
#         max_length=128)
#     transfected_notes = models.TextField(
#         blank=True,
#         help_text="Details on transfection methodology and details on genes or other genetic material introduced into assay")
#     serum = models.CharField(
#         max_length=128,
#         verbose_name="Percent serum")
#     dose_units = models.ForeignKey(
#         DoseUnits,
#         related_name='+')
#     dosing_notes = models.TextField()
#     observation_reported = models.BooleanField(
#         default=True)
#     observation_time = models.FloatField()
#     observation_time_units = models.PositiveSmallIntegerField(
#         choices=OBSERVATION_TIME_UNITS)
#     has_positive_control = models.BooleanField(
#         default=False)
#     positive_control = models.CharField(
#         max_length=128,
#         blank=True)
#     has_negative_control = models.BooleanField(
#         default=False)
#     negative_control = models.CharField(
#         max_length=128,
#         blank=True)
#     has_vehicle_control = models.BooleanField(
#         default=False)
#     vehicle_control = models.CharField(
#         max_length=128,
#         blank=True)
#     control_notes = models.TextField(
#         blank=True)


# class IVEndpoint(BaseEndpoint):

#     METABOLIC_ACTIVATION_CHOICES = (
#         (0, 'add'), )

#     VARIANCE_TYPE_CHOICES = (
#         (0, 'add'), )

#     MONOTONICITY_CHOICES = (
#         (0, 'add'), )

#     OVERALL_TREND_CHOICES = (
#         (0, 'add'), )

#     chemical = models.ForeignKey(
#         IVChemical,
#         related_name="endpoints")
#     experiment = models.ForeignKey(
#         IVExperiment,
#         related_name="experiments")
#     data_location = models.CharField(
#         max_length=128,
#         blank=True,
#         help_text="Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)")
#     effect_category = models.CharField(
#         max_length=128,
#         help_text="Standardized endpoint effect-category using controlled vocabulary")
#     effect = models.CharField(
#         max_length=128,
#         help_text="Standardized endpoint effect description using controlled vocabulary")
#     measured = models.CharField(
#         max_length=128,
#         help_text="Measured ")
#     short_description = models.CharField(
#         max_length=32,
#         help_text="Short (<32 character) description of effect & measurement")
#     metabolic_activation = models.PositiveSmallIntegerField(
#         choices=METABOLIC_ACTIVATION_CHOICES,
#         default=0)
#     response_units = models.CharField(
#         max_length=64,
#         verbose_name="Response units")
#     variance_type = models.PositiveSmallIntegerField(
#         default=0,
#         choices=VARIANCE_TYPE_CHOICES)
#     monotonicity = models.PositiveSmallIntegerField(
#         default=0,
#         choices=MONOTONICITY_CHOICES)
#     overall_trend = models.PositiveSmallIntegerField(
#         default=0,
#         choices=OVERALL_TREND_CHOICES)
#     statistical_test_notes = models.CharField(
#         max_length=256,
#         blank=True,
#         help_text="Notes describing details on the statistical tests performed")
#     NOAEL = models.SmallIntegerField(
#         verbose_name="NOAEL",
#         default=-999)
#     LOAEL = models.SmallIntegerField(
#         verbose_name="NOAEL",
#         default=-999)
#     endpoint_notes = models.TextField(
#         blank=True,
#         help_text="Any additional notes regarding the endpoint itself")
#     results_notes = models.TextField(
#         blank=True,
#         help_text="Qualitative description of the results")


# class IVEndpointGroup(models.Model):

#     SIGNIFICANCE_CHOICES = (
#         (0, 'add'), )

#     TREND_CHOICES = (
#         (0, 'add'), )

#     endpoint = models.ForeignKey(
#         IVEndpoint,
#         related_name="groups")
#     dose = models.FloatField(
#         validators=[MinValueValidator(0)])
#     trend = models.CharField(
#         choices=TREND_CHOICES,
#         default=0)
#     n = models.PositiveSmallIntegerField(
#         blank=True,
#         null=True,
#         validators=[MinValueValidator(1)])
#     significance = models.PositiveSmallIntegerField(
#         choices=SIGNIFICANCE_CHOICES,
#         default=0)
#     response = models.FloatField(
#         blank=True,
#         null=True)
#     variance = models.FloatField(
#         blank=True,
#         null=True,
#         validators=[MinValueValidator(0)])
#     cytotoxicity_observed = models.BooleanField(
#         default=False)

#     class Meta:
#         ordering = ('dose', )


# class IVCalculatedBenchmark(models.Model):
#     endpoint = models.ForeignKey(
#         IVEndpoint,
#         related_name="benchmark")
#     benchmark = models.CharField(
#         max_length=64)
#     value = models.FloatField(
#         validators=[MinValueValidator(0)])


# reversion.register(IVChemical)
# reversion.register(IVEndpoint)
# reversion.register(IVEndpointGroup)
# reversion.register(IVCalculatedBenchmark)
