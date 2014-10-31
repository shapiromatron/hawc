#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import logging

from django.core.validators import MinValueValidator
from django.core.cache import cache
from django.db import models

import reversion

from assessment.models import BaseEndpoint
from animal.models import DoseUnits
from utils.helper import HAWCDjangoJSONEncoder, build_tsv_file, build_excel_file
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

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'name', 'cas',
                  'cas_inferred', 'cas_notes', 'source',
                  'purity', 'purity_confirmed', 'purity_confirmed_notes',
                  'dilution_storage_notes')
        for field in fields:
            d[field] = getattr(self, field)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


class IVCellType(models.Model):

    SEX_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('mf', 'Male and female'),
        ('na', 'Not-applicable'),
        ('nr', 'Not-reported'))

    SEX_SYMBOL_CW = {
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

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'species', 'cell_type', 'tissue', 'source')
        for field in fields:
            d[field] = getattr(self, field)

        d['sex'] = self.get_sex_display()
        d['sex_symbol'] = IVCellType.SEX_SYMBOL_CW.get(self.sex)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


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

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'transfection', 'cell_line',
                  'dosing_notes', 'metabolic_activation', 'serum',
                  'has_positive_control', 'positive_control',
                  'has_negative_control', 'negative_control',
                  'has_vehicle_control', 'vehicle_control',
                  'control_notes')
        for field in fields:
            d[field] = getattr(self, field)

        d['metabolic_activation_symbol'] = self.get_metabolic_activation_display()
        d['dose_units'] = unicode(self.dose_units)
        d['study'] = self.study.get_json(json_encode=False)
        d['cell_type'] = self.cell_type.get_json(json_encode=False)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


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

    @staticmethod
    def get_cache_names(pks):
        return ['endpoint-json-{pk}'.format(pk=pk) for pk in pks]

    def get_json(self, json_encode=True):
        cache_name = IVEndpoint.get_cache_names([self.pk])[0]
        d = cache.get(cache_name)
        if d is None:

            d = {}
            fields = ('pk', 'name', 'assay_type',
                      'short_description', 'data_location', 'response_units',
                      'observation_time', 'NOAEL', 'LOAEL',
                      'statistical_test_notes', 'endpoint_notes', 'result_notes')
            for field in fields:
                d[field] = getattr(self, field)

            d['effects'] = list(self.effects.all().values_list('name', flat=True))
            d['data_type'] = self.get_data_type_display()
            d['variance_type'] = self.get_variance_type_display()
            d['observation_time_units'] = self.get_observation_time_units_display()
            d['monotonicity'] = self.get_monotonicity_display()
            d['overall_pattern'] = self.get_overall_pattern_display()
            d['trend_test'] = self.get_trend_test_display()
            d['additional_fields'] = json.loads(self.additional_fields)

            d['chemical'] = self.chemical.get_json(json_encode=False)
            d['experiment'] = self.experiment.get_json(json_encode=False)

            d['endpoint_groups'] = []
            for eg in self.groups.all():
                d['endpoint_groups'].append(eg.get_json(json_encode=False))

            d['benchmarks'] = []
            for bm in self.benchmarks.all():
                d['benchmarks'].append(bm.get_json(json_encode=False))

            logging.info('setting cache: {cache_name}'.format(cache_name=cache_name))
            cache.set(cache_name, d)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @classmethod
    def flat_file_header(cls, num_doses, num_bms):
        fields = [
            'Study',
            'Study HAWC ID',
            'Study identifier',
            'Study URL',
            'Chemical name',
            'Chemical CAS',
            'Chemical purity',
            'Cell species',
            'Cell sex',
            'Cell type',
            'Cell tissue',
            'Dose units',
            'Metabolic activation',
            'Transfection',
            'Cell line',
            'Endpoint HAWC ID',
            'Endpoint name',
            'Endpoint URL',
            'Endpoint description tags',
            'Assay type',
            'Endpoint description',
            'Endpoint response units',
            'Observation time',
            'Observation time units',
            'NOAEL',
            'LOAEL',
            'Monotonicity',
            'Overall pattern',
            'Trend test result',
            'Minimum dose',
            'Maximum dose'
        ]
        fields.extend(["Dose {0}".format(i)        for i in xrange(1, num_doses+1)])
        fields.extend(["Change Control {0}".format(i) for i in xrange(1, num_doses+1)])
        fields.extend(["Significant {0}".format(i) for i in xrange(1, num_doses+1)])

        fields.extend(["Benchmark Type {0}".format(i)  for i in xrange(1, num_bms+1)])
        fields.extend(["Benchmark Value {0}".format(i) for i in xrange(1, num_bms+1)])
        return fields

    def flat_file_row(self, num_doses, num_bms):
        d = self.get_json(json_encode=False)

        # get min and max doses or None
        min_dose = None
        max_dose = None
        doses = [ eg['dose'] for eg in d['endpoint_groups'] ]
        diffs = [ eg['difference_control']  for eg in d['endpoint_groups'] ]
        sigs  = [ eg['significant_control'] for eg in d['endpoint_groups'] ]
        if len(doses)>0:
            min_dose = min(d for d in doses if d>0)
            max_dose = max(doses)

        bm_types = [bm["benchmark"] for bm in d["benchmarks"]]
        bm_values = [bm["value"] for bm in d["benchmarks"]]

        row = [
                d['experiment']['study']['short_citation'],
                d['experiment']['study']['pk'],
                d['experiment']['study']['study_identifier'],
                d['experiment']['study']['study_url'],
                d['chemical']['name'],
                d['chemical']['cas'],
                d['chemical']['purity'],
                d['experiment']['cell_type']['species'],
                d['experiment']['cell_type']['sex'],
                d['experiment']['cell_type']['cell_type'],
                d['experiment']['cell_type']['tissue'],
                d['experiment']['dose_units'],
                d['experiment']['metabolic_activation'],
                d['experiment']['transfection'],
                d['experiment']['cell_line'],
                d['pk'],
                d['name'],
                'add URL',
                '|'.join(d['effects']),
                d['assay_type'],
                d['short_description'],
                d['response_units'],
                d['observation_time'],
                d['observation_time_units'],
                d['endpoint_groups'][d['NOAEL']]['dose'] if d['NOAEL'] != -999 else None,
                d['endpoint_groups'][d['LOAEL']]['dose'] if d['LOAEL'] != -999 else None,
                d['monotonicity'],
                d['overall_pattern'],
                d['trend_test'],
                min_dose,
                max_dose
        ]

        # extend rows to include blank placeholders, and apply
        doses.extend([None] * (num_doses-len(doses)))
        diffs.extend([None] * (num_doses-len(diffs)))
        sigs.extend([None] * (num_doses-len(sigs)))
        bm_types.extend([None] * (num_bms-len(bm_types)))
        bm_values.extend([None] * (num_bms-len(bm_values)))

        row.extend(doses)
        row.extend(diffs)
        row.extend(sigs)
        row.extend(bm_types)
        row.extend(bm_values)

        return [row]

    @classmethod
    def get_maximum_number_doses(cls, queryset):
        return max(queryset\
                            .annotate(max_egs=models.Count('groups'))\
                            .values_list('max_egs', flat=True))

    @classmethod
    def get_maximum_number_benchmarks(cls, queryset):
        return max(queryset\
                            .annotate(max_benchmarks=models.Count('benchmarks'))\
                            .values_list('max_benchmarks', flat=True))

    @classmethod
    def get_tsv_file(cls, queryset):
        """
        Construct a tab-delimited version of the selected queryset of endpoints.
        """
        num_doses = cls.get_maximum_number_doses(queryset)
        num_bms = cls.get_maximum_number_benchmarks(queryset)
        headers = cls.flat_file_header(num_doses=num_doses, num_bms=num_bms)
        return build_tsv_file(headers, queryset, num_doses=num_doses, num_bms=num_bms)

    @classmethod
    def get_excel_file(cls, queryset):
        """
        Construct an Excel workbook of the selected queryset of endpoints.
        """
        num_doses = cls.get_maximum_number_doses(queryset)
        num_bms = cls.get_maximum_number_benchmarks(queryset)
        sheet_name = 'in-vitro'
        data_rows_func = cls.build_excel_rows
        headers = cls.flat_file_header(num_doses=num_doses, num_bms=num_bms)
        return build_excel_file(sheet_name, headers, queryset, data_rows_func, num_doses=num_doses, num_bms=num_bms)

    @staticmethod
    def build_excel_rows(ws, queryset, *args, **kwargs):
        """
        Custom method used to build individual excel rows in Excel worksheet
        """
        # write data
        def try_float(str):
            # attempt to coerce as float, else return string
            try:
                return float(str)
            except:
                return str

        r = 1
        for endpoint in queryset:
            row = endpoint.flat_file_row(*args, **kwargs)
            for c, val in enumerate(row[0]):
                ws.write(r, c, try_float(val))
            r+=1


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

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'dose_group_id', 'dose',
                  'n', 'response', 'variance')
        for field in fields:
            d[field] = getattr(self, field)

        d['difference_control'] = self.get_difference_control_display()
        d['significant_control'] = self.get_significant_control_display()
        d['cytotoxicity_observed'] = self.get_cytotoxicity_observed_display()

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


class IVBenchmark(models.Model):
    endpoint = models.ForeignKey(
        IVEndpoint,
        related_name="benchmarks")
    benchmark = models.CharField(
        max_length=32)
    value = models.FloatField(
        validators=[MinValueValidator(0)])

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'benchmark', 'value')
        for field in fields:
            d[field] = getattr(self, field)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


reversion.register(IVChemical)
reversion.register(IVCellType)
reversion.register(IVExperiment)
reversion.register(IVEndpoint)
reversion.register(IVEndpointGroup)
reversion.register(IVBenchmark)
