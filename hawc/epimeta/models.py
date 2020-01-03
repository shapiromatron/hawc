#!/usr/bin/env python
# -*- coding: utf8 -*-
import json

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

from reversion import revisions as reversion

from assessment.serializers import AssessmentSerializer
from epi.models import Criteria, ResultMetric, AdjustmentFactor
from study.models import Study
from utils.helper import SerializerHelper, HAWCDjangoJSONEncoder
from utils.models import get_crumbs

from . import managers


class MetaProtocol(models.Model):
    objects = managers.MetaProtocolManager()

    META_PROTOCOL_CHOICES = (
        (0, "Meta-analysis"),
        (1, "Pooled-analysis"))

    META_LIT_SEARCH_CHOICES = (
        (0, "Systematic"),
        (1, "Other"))

    study = models.ForeignKey(
        'study.Study',
        related_name="meta_protocols")
    name = models.CharField(
        verbose_name="Protocol name",
        max_length=128)
    protocol_type = models.PositiveSmallIntegerField(
        choices=META_PROTOCOL_CHOICES,
        default=0)
    lit_search_strategy = models.PositiveSmallIntegerField(
        verbose_name="Literature search strategy",
        choices=META_LIT_SEARCH_CHOICES,
        default=0)
    lit_search_notes = models.TextField(
        verbose_name="Literature search notes",
        blank=True)
    lit_search_start_date = models.DateField(
        verbose_name="Literature search start-date",
        blank=True,
        null=True)
    lit_search_end_date = models.DateField(
        verbose_name="Literature search end-date",
        blank=True,
        null=True)
    total_references = models.PositiveIntegerField(
        verbose_name="Total number of references found",
        help_text="References identified through initial literature-search "
                  "before application of inclusion/exclusion criteria",
        blank=True,
        null=True)
    inclusion_criteria = models.ManyToManyField(
        Criteria,
        related_name='meta_inclusion_criteria',
        blank=True)
    exclusion_criteria = models.ManyToManyField(
        Criteria,
        related_name='meta_exclusion_criteria',
        blank=True)
    total_studies_identified = models.PositiveIntegerField(
        verbose_name="Total number of studies identified",
        help_text="Total references identified for inclusion after application "
                  "of literature review and screening criteria")
    notes = models.TextField(blank=True)

    COPY_NAME = 'meta_protocol'

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.study.get_assessment()

    def get_crumbs(self):
        return get_crumbs(self, self.study)

    def get_absolute_url(self):
        return reverse('meta:protocol_detail', kwargs={'pk': self.pk})

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode, from_cache=False)

    def copy_across_assessments(self, cw):
        children = list(self.results.all())
        old_id = self.id
        self.id = None
        self.study_id = cw[Study.COPY_NAME][self.study_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id
        for child in children:
            child.copy_across_assessments(cw)


    @staticmethod
    def flat_complete_header_row():
        return (
            'meta_protocol-pk',
            'meta_protocol-url',
            'meta_protocol-name',
            'meta_protocol-protocol_type',
            'meta_protocol-lit_search_strategy',
            'meta_protocol-lit_search_notes',
            'meta_protocol-lit_search_start_date',
            'meta_protocol-lit_search_end_date',
            'meta_protocol-total_references',
            'meta_protocol-inclusion_criteria',
            'meta_protocol-exclusion_criteria',
            'meta_protocol-total_studies_identified',
            'meta_protocol-notes',
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['name'],
            ser['protocol_type'],
            ser['lit_search_strategy'],
            ser['lit_search_notes'],
            ser['lit_search_start_date'],
            ser['lit_search_end_date'],
            ser['total_references'],
            '|'.join(ser['inclusion_criteria']),
            '|'.join(ser['exclusion_criteria']),
            ser['total_studies_identified'],
            ser['notes']
        )

    def get_study(self):
        return self.study


class MetaResult(models.Model):
    objects = managers.MetaResultManager()

    protocol = models.ForeignKey(
        MetaProtocol,
        related_name="results")
    label = models.CharField(
        max_length=128)
    data_location = models.CharField(
        max_length=128,
        blank=True,
        help_text="Details on where the data are found in the literature "
                  "(ex: Figure 1, Table 2, etc.)")
    health_outcome = models.CharField(
        max_length=128)
    health_outcome_notes = models.TextField(
        blank=True)
    exposure_name = models.CharField(
        max_length=128)
    exposure_details = models.TextField(
        blank=True)
    number_studies = models.PositiveSmallIntegerField()
    metric = models.ForeignKey(
        ResultMetric)
    statistical_notes = models.TextField(
        blank=True)
    n = models.PositiveIntegerField(
        help_text="Number of individuals included from all analyses")
    estimate = models.FloatField()
    heterogeneity = models.CharField(
        max_length=256,
        blank=True)
    lower_ci = models.FloatField(
        verbose_name="Lower CI",
        help_text="Numerical value for lower-confidence interval")
    upper_ci = models.FloatField(
        verbose_name="Upper CI",
        help_text="Numerical value for upper-confidence interval")
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name='Confidence Interval (CI)',
        help_text='A 95% CI is written as 0.95.')
    adjustment_factors = models.ManyToManyField(
        AdjustmentFactor,
        help_text="All factors which were included in final model",
        related_name='meta_adjustments',
        blank=True)
    notes = models.TextField(
        blank=True)

    COPY_NAME = 'meta_result'

    class Meta:
        ordering = ('label', )

    def __str__(self):
        return self.label

    def get_crumbs(self):
        return get_crumbs(self, self.protocol)

    def get_assessment(self):
        return self.protocol.get_assessment()

    def get_absolute_url(self):
        return reverse('meta:result_detail', kwargs={'pk': self.pk})

    @property
    def estimate_formatted(self):
        txt = "-"
        if self.estimate:
            txt = str(self.estimate)
        if (self.lower_ci and self.upper_ci):
            txt += ' ({}, {})'.format(self.lower_ci, self.upper_ci)
        return txt

    @classmethod
    def delete_caches(cls, pks):
        SerializerHelper.delete_caches(cls, pks)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @staticmethod
    def get_qs_json(queryset, json_encode=True):
        results = [result.get_json(json_encode=False) for result in queryset]
        if json_encode:
            return json.dumps(results, cls=HAWCDjangoJSONEncoder)
        else:
            return results

    @staticmethod
    def flat_complete_header_row():
        return (
            'meta_result-pk',
            'meta_result-url',
            'meta_result-label',
            'meta_result-data_location',
            'meta_result-health_outcome',
            'meta_result-health_outcome_notes',
            'meta_result-exposure_name',
            'meta_result-exposure_details',
            'meta_result-number_studies',
            'meta_result-statistical_metric',
            'meta_result-statistical_notes',
            'meta_result-n',
            'meta_result-estimate',
            'meta_result-lower_ci',
            'meta_result-upper_ci',
            'meta_result-ci_units',
            'meta_result-heterogeneity',
            'meta_result-adjustment_factors',
            'meta_result-notes',
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['url'],
            ser['label'],
            ser['data_location'],
            ser['health_outcome'],
            ser['health_outcome_notes'],
            ser['exposure_name'],
            ser['exposure_details'],
            ser['number_studies'],
            ser['metric']['metric'],
            ser['statistical_notes'],
            ser['n'],
            ser['estimate'],
            ser['lower_ci'],
            ser['upper_ci'],
            ser['ci_units'],
            ser['heterogeneity'],
            '|'.join(ser['adjustment_factors']),
            ser['notes'],
        )

    @staticmethod
    def get_docx_template_context(assessment, queryset):
        """
        Given a queryset of meta-results, invert the cached results to build
        a top-down data hierarchy from study to meta-result. We use this
        approach since our meta-results are cached, so while it may require
        more computation, its close to free on database access.
        """

        def getStatMethods(mr):
            key = "{}|{}".format(
                mr["adjustments_list"],
                mr["statistical_notes"]
            )
            return key, mr

        results = [
            SerializerHelper.get_serialized(obj, json=False)
            for obj in queryset
        ]
        studies = {}

        # flip dictionary nesting
        for thisMr in results:
            thisPro = thisMr["protocol"]
            thisStudy = thisMr["protocol"]["study"]

            study = studies.get(thisStudy["id"])
            if study is None:
                study = thisStudy
                study["protocols"] = {}
                studies[study["id"]] = study

            pro = study["protocols"].get(thisPro["id"])
            if pro is None:
                pro = thisPro
                pro["inclusion_list"] = ', '.join(pro["inclusion_criteria"])
                pro["exclusion_list"] = ', '.join(pro["exclusion_criteria"])
                pro["results"] = {}
                pro["statistical_methods"] = {}
                study["protocols"][pro["id"]] = pro

            mr = pro["results"].get(thisMr["id"])
            if mr is None:
                mr = thisMr
                mr["ci_percent"] = int(mr["ci_units"] * 100.)
                mr["adjustments_list"] = ', '.join(
                    sorted(mr["adjustment_factors"]))
                pro["results"][mr["id"]] = mr

            statKey, statVal = getStatMethods(thisMr)
            stats = pro["statistical_methods"].get(statKey)
            if stats is None:
                stats = statVal
                pro["statistical_methods"][statKey] = statVal
                stats["sm_endpoints"] = []
            stats["sm_endpoints"].append(thisMr)

        # convert value dictionaries to lists
        studies = sorted(
            list(studies.values()),
            key=lambda obj: (obj["short_citation"].lower()))
        for study in studies:
            study["protocols"] = sorted(
                list(study["protocols"].values()),
                key=lambda obj: (obj["name"].lower()))
            for pro in study["protocols"]:
                pro["results"] = sorted(
                    list(pro["results"].values()),
                    key=lambda obj: (obj["label"].lower()))
                pro["statistical_methods"] = list(pro["statistical_methods"].values())
                for obj in pro["statistical_methods"]:
                    obj["sm_endpoints"] = "; ".join([
                        d["label"] for d in obj["sm_endpoints"]
                    ])

        return {
            "assessment": AssessmentSerializer().to_representation(assessment),
            "studies": studies
        }

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.protocol_id = cw[MetaProtocol.COPY_NAME][self.protocol_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id

    def get_study(self):
        if self.protocol is not None:
            return self.protocol.get_study()


class SingleResult(models.Model):
    objects = managers.SingleResultManager()

    meta_result = models.ForeignKey(
        MetaResult,
        related_name="single_results")
    study = models.ForeignKey(
        'study.Study',
        related_name="single_results",
        blank=True,
        null=True)
    exposure_name = models.CharField(
        max_length=128,
        help_text='Enter a descriptive-name for the single study result '
                  '(e.g., "Smith et al. 2000, obese-males")')
    weight = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="For meta-analysis, enter the fraction-weight assigned for "
                  "each result (leave-blank for pooled analyses)")
    n = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Enter the number of observations for this result")
    estimate = models.FloatField(
        blank=True,
        null=True,
        help_text="Enter the numerical risk-estimate presented for this result")
    lower_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Lower CI",
        help_text="Numerical value for lower-confidence interval")
    upper_ci = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Upper CI",
        help_text="Numerical value for upper-confidence interval")
    ci_units = models.FloatField(
        blank=True,
        null=True,
        default=0.95,
        verbose_name='Confidence Interval (CI)',
        help_text='A 95% CI is written as 0.95.')
    notes = models.TextField(
        blank=True)

    COPY_NAME = 'meta_single_result'

    class Meta:
        ordering = ('exposure_name', )

    def __str__(self):
        return self.exposure_name

    @property
    def estimate_formatted(self):
        txt = "-"
        if self.estimate:
            txt = str(self.estimate)
        if (self.lower_ci and self.upper_ci):
            txt += ' ({}, {})'.format(self.lower_ci, self.upper_ci)
        return txt

    @staticmethod
    def flat_complete_header_row():
        return (
            'single_result-pk',
            'single_result-study',
            'single_result-exposure_name',
            'single_result-weight',
            'single_result-n',
            'single_result-estimate',
            'single_result-lower_ci',
            'single_result-upper_ci',
            'single_result-ci_units',
            'single_result-notes',
        )

    @staticmethod
    def flat_complete_data_row(ser):

        study = None
        try:
            study = ser['study']['id']
        except TypeError:
            pass

        return (
            ser['id'],
            study,
            ser['exposure_name'],
            ser['weight'],
            ser['n'],
            ser['estimate'],
            ser['lower_ci'],
            ser['upper_ci'],
            ser['ci_units'],
            ser['notes'],
        )

    def copy_across_assessments(self, cw):
        old_id = self.id
        self.id = None
        self.meta_result_id = cw[MetaResult.COPY_NAME][self.meta_result_id]
        self.study_id = cw[Study.COPY_NAME][self.study_id]
        self.save()
        cw[self.COPY_NAME][old_id] = self.id

    def get_study(self):
        if self.meta_result is not None:
            return self.meta_result.get_study()


reversion.register(
    MetaProtocol,
    follow=('inclusion_criteria', 'exclusion_criteria')
)
reversion.register(
    MetaResult,
    follow=('adjustment_factors', 'single_results')
)
reversion.register(
    SingleResult
)
