#!/usr/bin/env python
# -*- coding: utf8 -*-
import json
import logging

from django.core.cache import cache
from django.core.urlresolvers import reverse
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

SEX_CHOICES = (
    ('m', 'Male'),
    ('f', 'Female'),
    ('b', 'Male and female'),
    ('na', 'Not-applicable'),
    ('nr', 'Not-reported'))

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


class CellType(models.Model):
    name = models.CharField(max_length=256, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Experiment(models.Model):
    study = models.ForeignKey('study.Study', related_name='ivexperiments')
    species = models.ForeignKey(Species)
    strain = models.ForeignKey(Strain, blank=True, null=True)
    sex = models.CharField(max_length=2, choices=SEX_CHOICES)
    cell_type = models.ForeignKey(CellType)
    evidence_stream = models.CharField(max_length=1, choices=EVIDENCE_STREAM_CHOICES)
    generation = models.CharField(max_length=2, choices=GENERATION_CHOICES)
    dose_units = models.ForeignKey(DoseUnits)
    treatment_period = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return unicode(self.cell_type)

    @property
    def sex_symbol(self):
        return SEX_SYMBOL_CW[self.sex]

    def get_absolute_url(self):
        return reverse('invitro:experiment_detail', kwargs={'pk': self.pk})

    def get_assessment(self):
        return self.study.get_assessment()

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'treatment_period')
        for field in fields:
            d[field] = getattr(self, field)

        d['url'] = self.get_absolute_url()
        d['species'] = self.species.__unicode__()
        if self.strain:
            d['strain'] = self.strain.__unicode__()
        d['sex'] = self.sex_symbol
        d['cell_type'] = self.cell_type.__unicode__()
        d['evidence_stream'] = self.get_evidence_stream_display()
        d['generation'] = self.get_generation_display()
        d['dose_units'] = self.dose_units.__unicode__()

        # child details
        egs = []
        for eg in self.exposure_groups.all():
            egs.append(eg.get_json(json_encode=False))
        d['egs'] = egs

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


class ExposureGroup(models.Model):
    experiment = models.ForeignKey(Experiment, related_name='exposure_groups')
    group_id = models.PositiveSmallIntegerField()
    dose = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('group_id', )

    def __unicode__(self):
        return str(self.dose)

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'group_id', 'dose')
        for field in fields:
            d[field] = getattr(self, field)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d


class IVEndpoint(BaseEndpoint):
    experiment = models.ForeignKey(Experiment, related_name='endpoints')
    diagnostic = models.CharField(max_length=256)
    response_units = models.CharField(max_length=128)
    data_type = models.CharField(max_length=2, choices=DATA_TYPE_CHOICES)
    direction_of_effect = models.CharField(max_length=2, choices=EFFECT_DIRECTION_CHOICES)
    loael = models.SmallIntegerField(default=-999)
    noael = models.SmallIntegerField(default=-999)
    target_process = models.CharField(max_length=256,
                                      verbose_name="Target Tissue/Physiological Process")
    data_extracted = models.BooleanField(default=True,
        help_text="Dose-response data for endpoint are extracted in HAWC")
    response_trend = models.CharField(max_length=2, choices=RESPONSE_TREND_CHOICES)

    def get_assessment(self):
        return self.assessment

    def get_absolute_url(self):
        return reverse('invitro:endpoint_detail', kwargs={'pk': self.pk})

    def get_json(self, json_encode=True):
        cache_name = 'endpoint-json-{pk}'.format(pk=self.pk)
        d = cache.get(cache_name)
        if d is None:
            d = {}

            # parent details
            d['experiment'] = self.experiment.get_json(json_encode=False)
            d['study'] = self.experiment.study.get_json(json_encode=False)

            # self details
            fields = ('pk', 'name', 'diagnostic', 'response_units',
                      'target_process', 'data_extracted', 'loael', 'noael')
            for field in fields:
                d[field] = getattr(self, field)

            d['endpoint_type'] = 'in-vitro'
            d['url'] = self.get_absolute_url()
            d['data_type'] = self.get_data_type_display()
            d['direction_of_effect'] = self.direction_of_effect_symbol
            d['direction_of_effect_text'] = self.get_direction_of_effect_display()
            d['response_trend'] = self.get_response_trend_display()

            def get_dose_index(idx, exp_list):
                # get dose-value instead of index for effect, or "-"
                try:
                    return exp_list[idx]['dose']
                except IndexError:
                    return "-"

            d['NOAEL_dose'] = get_dose_index(self.noael, d['experiment']['egs'])
            d['LOAEL_dose'] = get_dose_index(self.loael, d['experiment']['egs'])

            def get_dose_summary(exp_list, noael, loael):
                # comma-separated list with * for noael/loael values
                vals = []
                for i, dose in enumerate(exp_list[1:]):
                    val = str(dose['dose'])
                    if i+1 in [noael, loael]:  # fix index since we slice above
                        val += "*"
                    vals.append(val)
                return ', '.join(vals)

            d['dose_summary'] = get_dose_summary(d['experiment']['egs'],
                                                 self.noael, self.loael)

            # child details
            egs = []
            for eg in self.groups.all():
                egs.append(eg.get_json(json_encode=False))
            d['egs'] = egs

            logging.info('setting cache: {cache_name}'.format(cache_name=cache_name))
            cache.set(cache_name, d)

        # return format
        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

    @property
    def direction_of_effect_symbol(self):
        return DIR_EFFECT_SYMBOL_CW[self.direction_of_effect]

    def flat_file_row(self):
        d = self.get_json(json_encode=False)
        num_doses = len(d['experiment']['egs'])
        row = [
            d['study']['short_citation'],
            d['study']['study_url'],
            d['study']['pk'],

            d['experiment']['pk'],
            d['experiment']['url'],
            d['experiment']['species'],
            d['experiment'].get('strain', None),
            d['experiment']['sex'],
            d['experiment']['cell_type'],
            d['experiment']['evidence_stream'],
            d['experiment']['generation'],
            d['experiment']['dose_units'],
            d['experiment']['treatment_period'],

            d['experiment']['egs'][1]['dose'],
            d['experiment']['egs'][num_doses-1]['dose'],
        ]

        row.extend([x['dose'] for x in d['experiment']['egs']])
        row.extend(['-']*(8-num_doses))

        row.extend([
            d['pk'],
            d['url'],
            d['name'],
            d['data_type'],
            d['diagnostic'],
            d['direction_of_effect'],
            d['response_trend'],
            d['response_units'],
            d['NOAEL_dose'],
            d['LOAEL_dose'],
            d['dose_summary']
        ])

        return [row]

    @classmethod
    def flat_file_header(cls):
        return [
                'Study',
                'Study URL',
                'Study Primary Key',

                'Experiment Primary Key',
                'Experiment URL',
                'Species',
                'Strain',
                'Sex',
                'Cell Type',
                'Evidence Stream',
                'Generation',
                'Dose Units',
                'Treatment Period',

                'Min Non-zero Dose',
                'Max Non-zero Dose',
                'Dose 1',
                'Dose 2',
                'Dose 3',
                'Dose 4',
                'Dose 5',
                'Dose 6',
                'Dose 7',
                'Dose 8',

                'Endpoint Primary Key',
                'Endpoint URL',
                'Endpoint',
                'Data Type',
                'Diagnostic',
                'Direction of Effect',
                'Response Trend',
                'Response Units',
                'NOAEL',
                'LOAEL',
                'Dose Summary'
            ]

    @classmethod
    def get_tsv_file(cls, queryset):
        """
        Construct a tab-delimited version of the selected queryset of endpoints.
        """
        headers = IVEndpoint.flat_file_header()
        return build_tsv_file(headers, queryset)

    @classmethod
    def get_excel_file(cls, queryset):
        """
        Construct an Excel workbook of the selected queryset of endpoints.
        """
        sheet_name = 'in-vitro'
        headers = IVEndpoint.flat_file_header()
        data_rows_func = IVEndpoint.build_excel_rows
        return build_excel_file(sheet_name, headers, queryset, data_rows_func)

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

        row = 0
        for iv in queryset:
            row+=1
            for j, val in enumerate(iv.flat_file_row()[0]):
                ws.write(row, j, try_float(val))


class EndpointGroup(models.Model):
    endpoint = models.ForeignKey(IVEndpoint, related_name='groups')
    exposure_group = models.ForeignKey(ExposureGroup)
    n = models.PositiveSmallIntegerField()
    response = models.FloatField(blank=True, null=True)
    stdev = models.FloatField(blank=True, null=True)
    incidence = models.PositiveSmallIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_json(self, json_encode=True):
        d = {}
        fields = ('pk', 'n', 'response', 'stdev', 'incidence')
        for field in fields:
            d[field] = getattr(self, field)

        if json_encode:
            return json.dumps(d, cls=HAWCDjangoJSONEncoder)
        else:
            return d

reversion.register(CellType)
reversion.register(Experiment, follow=('exposure_groups'))
reversion.register(ExposureGroup)
reversion.register(IVEndpoint, follow=('groups'))
reversion.register(EndpointGroup)
