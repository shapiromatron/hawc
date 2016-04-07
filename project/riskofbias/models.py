from __future__ import unicode_literals
import json
import os
from collections import OrderedDict

from django.db import models
from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from reversion import revisions as reversion

from myuser.models import HAWCUser
from utils.helper import cleanHTML


class RiskOfBiasDomain(models.Model):
    assessment = models.ForeignKey('assessment.Assessment',
    related_name="sq_domains")
    name = models.CharField(max_length=128)
    description = models.TextField(default="")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assessment', 'name')
        ordering = ('pk', )

    def __unicode__(self):
        return self.name

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_default(cls, assessment):
        """
        Construct default risk of bias domains/metrics for an assessment.
        The risk-of-bias domains and metrics are those defined by NTP/OHAT
        protocols for risk-of-bias
        """
        fn = os.path.join(settings.PROJECT_PATH, 'study/fixtures/ohat_study_quality_defaults.json')
        with open(fn, 'r') as f:
            objects = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)

            for domain in objects["domains"]:
                d = RiskOfBiasDomain(assessment=assessment,
                name=domain["name"],
                description=domain["description"])
                d.save()
                RiskOfBiasMetric.build_metrics_for_one_domain(d, domain["metrics"])


class RiskOfBiasMetric(models.Model):
    domain = models.ForeignKey(RiskOfBiasDomain,
                               related_name="metrics")
    metric = models.CharField(max_length=256)
    description = models.TextField(blank=True,
                                   help_text='HTML text describing scoring of this field.')
    required_animal = models.BooleanField(
        default=True,
        verbose_name="Required for bioassay?",
        help_text="Is this metric required for animal bioassay studies?")
    required_epi = models.BooleanField(
        default=True,
        verbose_name="Required for epidemiology?",
        help_text="Is this metric required for human epidemiological studies?")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('domain', 'id')

    def __unicode__(self):
        return self.metric

    def get_assessment(self):
        return self.domain.get_assessment()

    @classmethod
    def get_required_metrics(self, assessment, study):
        filters = {
            "domain__in": RiskOfBiasDomain.objects.filter(assessment=assessment),
        }
        if study.study_type == 0:
            filters["required_animal"] = True
        elif study.study_type in [1,4]:
            filters["required_epi"] = True
        return RiskOfBiasMetric.objects.filter(**filters)

    @classmethod
    def build_metrics_for_one_domain(cls, domain, metrics):
        """
        Build multiple risk-of-bias metrics given a domain django object and a
        list of python dictionaries for each metric.
        """
        objs = []
        for metric in metrics:
            obj = RiskOfBiasMetric(**metric)
            obj.domain = domain
            objs.append(obj)
        RiskOfBiasMetric.objects.bulk_create(objs)


class RiskOfBias(models.Model):

    RISK_OF_BIAS_SCORE_CHOICES = (
        (1, 'Definitely high risk of bias'),
        (2, 'Probably high risk of bias'),
        (3, 'Probably low risk of bias'),
        (4, 'Definitely low risk of bias'),
        (0, 'Not applicable'))

    SCORE_SYMBOLS = {
        1: "--",
        2: "-",
        3: "+",
        4: "++",
        0: "-",
    }

    SCORE_SHADES = {
        1: "#CC3333",
        2: "#FFCC00",
        3: "#6FFF00",
        4: "#00CC00",
        0: "#FFCC00",
    }

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    metric = models.ForeignKey(RiskOfBiasMetric, related_name='qualities')
    score = models.PositiveSmallIntegerField(choices=RISK_OF_BIAS_SCORE_CHOICES, default=4)
    notes = models.TextField(blank=True, default="")
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(HAWCUser,
        related_name='qualities',
        blank=True,
        null=True)

    class Meta:
        ordering = ("content_type", "object_id", "metric")
        verbose_name_plural = "Risk of Biases"
        unique_together = (("content_type", "object_id", "metric"), )

    def __unicode__(self):
        return '{}: {}'.format(self.metric, self.score)

    def get_assessment(self):
        return self.content_object.get_assessment()

    def get_absolute_url(self):
        if type(self.content_object) is Study:
            return reverse('riskofbias:robs_detail', args=[str(self.study.pk)])
        else:
            return self.content_object.get_absolute_url()

    def get_edit_url(self):
        return reverse('riskofbias:rob_update', args=[self.pk])

    def get_delete_url(self):
        return reverse('riskofbias:rob_delete', args=[self.pk])

    @property
    def score_symbol(self):
        return self.SCORE_SYMBOLS[self.score]

    @property
    def score_shade(self):
        return self.SCORE_SHADES[self.score]

    @staticmethod
    def flat_complete_header_row():
        return (
            'sq-domain_id',
            'sq-domain_name',
            'sq-domain_description',
            'sq-metric_id',
            'sq-metric_metric',
            'sq-metric_description',
            'sq-id',
            'sq-notes',
            'sq-score_description',
            'sq-score'
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['metric']['domain']['id'],
            ser['metric']['domain']['name'],
            ser['metric']['domain']['description'],
            ser['metric']['id'],
            ser['metric']['metric'],
            ser['metric']['description'],
            ser['id'],
            cleanHTML(ser['notes']),
            ser['score_description'],
            ser['score']
        )
