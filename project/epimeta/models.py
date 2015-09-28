#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

import reversion

from assessment.serializers import AssessmentSerializer
from epi2.models import Criteria, ResultMetric, AdjustmentFactor
from utils.helper import SerializerHelper
from utils.models import get_crumbs


class MetaProtocol(models.Model):

    META_PROTOCOL_CHOICES = (
        (0, "Meta-analysis"),
        (1, "Pooled-analysis"))

    META_LIT_SEARCH_CHOICES = (
        (0, "Systematic"),
        (1, "Other"))

    study = models.ForeignKey('study.Study',
        related_name="meta_protocols2")
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

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name

    def get_assessment(self):
        return self.study.get_assessment()

    def get_crumbs(self):
        return get_crumbs(self, self.study)

    def get_absolute_url(self):
        return reverse('meta:protocol_detail', kwargs={'pk': self.pk})

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode, from_cache=False)

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
            u'|'.join(ser['inclusion_criteria']),
            u'|'.join(ser['exclusion_criteria']),
            ser['total_studies_identified'],
            ser['notes']
        )


class MetaResult(models.Model):
    protocol = models.ForeignKey(
        MetaProtocol,
        related_name="results2")
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

    class Meta:
        ordering = ('label', )

    def __unicode__(self):
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
            txt = unicode(self.estimate)
        if (self.lower_ci and self.upper_ci):
            txt += u' ({}, {})'.format(self.lower_ci, self.upper_ci)
        return txt

    @classmethod
    def delete_caches(cls, pks):
        SerializerHelper.delete_caches(cls, pks)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

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
            u'|'.join(ser['adjustment_factors']),
            ser['notes'],
        )

    @classmethod
    def get_docx_template_context(cls, assessment, queryset):
        """
        Given a queryset of meta-results, invert the cached results to build
        a top-down data hierarchy from study to meta-result. We use this
        approach since our meta-results are cached, so while it may require
        more computation, its close to free on database access.
        """

        def getStatMethods(mr):
            key = u"{}|{}".format(
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
                pro["inclusion_list"] = u', '.join(pro["inclusion_criteria"])
                pro["exclusion_list"] = u', '.join(pro["exclusion_criteria"])
                pro["results"] = {}
                pro["statistical_methods"] = {}
                study["protocols"][pro["id"]]  = pro

            mr = pro["results"].get(thisMr["id"])
            if mr is None:
                mr = thisMr
                mr["ci_percent"] = int(mr["ci_units"]*100.)
                mr["adjustments_list"] = u', '.join(sorted(mr["adjustment_factors"]))
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
            studies.values(),
            key=lambda obj: (obj["short_citation"].lower()))
        for study in studies:
            study["protocols"] = sorted(
                study["protocols"].values(),
                key=lambda obj: (obj["name"].lower()))
            for pro in study["protocols"]:
                pro["results"] = sorted(
                    pro["results"].values(),
                    key=lambda obj: (obj["label"].lower()))
                pro["statistical_methods"] = pro["statistical_methods"].values()
                for obj in pro["statistical_methods"]:
                    obj["sm_endpoints"] = u"; ".join([ d["label"] for d in obj["sm_endpoints"] ])

        return {
            "assessment": AssessmentSerializer().to_representation(assessment),
            "studies": studies
        }


class SingleResult(models.Model):
    meta_result = models.ForeignKey(
        MetaResult,
        related_name="single_results2")
    study = models.ForeignKey(
        'study.Study',
        related_name="single_results2",
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

    def __unicode__(self):
        return self.exposure_name

    @property
    def estimate_formatted(self):
        txt = "-"
        if self.estimate:
            txt = unicode(self.estimate)
        if (self.lower_ci and self.upper_ci):
            txt += u' ({}, {})'.format(self.lower_ci, self.upper_ci)
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


@receiver(post_save, sender=MetaProtocol)
@receiver(pre_delete, sender=MetaProtocol)
@receiver(post_save, sender=MetaResult)
@receiver(pre_delete, sender=MetaResult)
@receiver(post_save, sender=SingleResult)
@receiver(pre_delete, sender=SingleResult)
def invalidate_meta_result_cache(sender, instance, **kwargs):
    instance_type = type(instance)
    filters = {}
    if instance_type is MetaProtocol:
        filters["protocol"] = instance.id
    elif instance_type is MetaResult:
        ids = [instance.id]
    elif instance_type is SingleResult:
        ids = [instance.meta_result_id]

    if len(filters) > 0:
        ids = MetaResult.objects.filter(**filters).values_list('id', flat=True)

    MetaResult.delete_caches(ids)


reversion.register(MetaProtocol,
    follow=('inclusion_criteria', 'exclusion_criteria'))
reversion.register(MetaResult, follow=('adjustment_factors', ))
reversion.register(SingleResult)
