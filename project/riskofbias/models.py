from __future__ import unicode_literals
import json
import os
import collections

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from reversion import revisions as reversion

from assessment.models import Assessment
from myuser.models import HAWCUser
from study.models import Study
from utils.helper import cleanHTML, SerializerHelper
from utils.models import get_crumbs


class RiskOfBiasDomain(models.Model):
    assessment = models.ForeignKey(
        'assessment.Assessment',
        related_name='rob_domains')
    name = models.CharField(
        max_length=128)
    description = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

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
        The risk of bias domains and metrics are those defined by NTP/OHAT
        protocols for risk of bias
        """
        fn = os.path.join(
            settings.PROJECT_PATH,
            'riskofbias/fixtures/ohat_study_quality_defaults.json'
        )
        with open(fn, 'r') as f:
            objects = json.loads(
                f.read(),
                object_pairs_hook=collections.OrderedDict)

        for domain in objects['domains']:
            d = RiskOfBiasDomain.objects.create(
                assessment=assessment,
                name=domain['name'],
                description=domain['description'])
            RiskOfBiasMetric.build_metrics_for_one_domain(d, domain['metrics'])

    @classmethod
    def assessment_qs(cls, assessment_id):
        return cls.objects.filter(assessment=assessment_id)


class RiskOfBiasMetric(models.Model):
    domain = models.ForeignKey(
        RiskOfBiasDomain,
        related_name='metrics')
    metric = models.CharField(
        max_length=256)
    description = models.TextField(
        blank=True,
        help_text='HTML text describing scoring of this field.')
    required_animal = models.BooleanField(
        default=True,
        verbose_name='Required for bioassay?',
        help_text='Is this metric required for animal bioassay studies?')
    required_epi = models.BooleanField(
        default=True,
        verbose_name='Required for epidemiology?',
        help_text='Is this metric required for human epidemiological studies?')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('domain', 'id')

    def __unicode__(self):
        return self.metric

    def get_assessment(self):
        return self.domain.get_assessment()

    @classmethod
    def assessment_qs(cls, assessment_id):
        return cls.objects.filter(domain__assessment=assessment_id)

    @classmethod
    def get_required_metrics(cls, assessment, study):

        requireds = models.Q()
        if study.bioassay:
            requireds |= models.Q(required_animal=True)
        if study.epi or study.epi_meta:
            requireds |= models.Q(required_epi=True)

        return RiskOfBiasMetric.objects\
            .filter(domain__assessment=assessment)\
            .filter(requireds)

    @classmethod
    def build_metrics_for_one_domain(cls, domain, metrics):
        """
        Build multiple risk of bias metrics given a domain django object and a
        list of python dictionaries for each metric.
        """
        objs = []
        for metric in metrics:
            obj = RiskOfBiasMetric(**metric)
            obj.domain = domain
            objs.append(obj)
        RiskOfBiasMetric.objects.bulk_create(objs)

    @classmethod
    def get_metrics_for_visuals(cls, assessment_id):
        return cls.objects\
            .filter(domain__assessment_id=assessment_id)\
            .values('id', 'metric')


class RiskOfBias(models.Model):
    study = models.ForeignKey(
        'study.Study',
        related_name='riskofbiases',
        null=True)
    final = models.BooleanField(
        default=False,
        db_index=True)
    author = models.ForeignKey(
        HAWCUser,
        related_name='riskofbiases')
    active = models.BooleanField(
        default=False,
        db_index=True)
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    class Meta:
        verbose_name_plural = 'Risk of Biases'
        ordering = ('final',)

    def __unicode__(self):
        return '{} (Risk of bias)'.format(self.study.short_citation)

    def get_assessment(self):
        return self.study.get_assessment()

    @classmethod
    def assessment_qs(cls, assessment_id):
        return cls.objects.filter(study__assessment=assessment_id)

    def get_final_url(self):
        return reverse('riskofbias:rob_detail', args=[self.study_id])

    def get_absolute_url(self):
        return reverse('riskofbias:arob_reviewers',
            args=[self.get_assessment().pk])

    def get_edit_url(self):
        return reverse('riskofbias:rob_update', args=[self.pk])

    def get_crumbs(self):
        return get_crumbs(self, self.study)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def build_scores(self, assessment, study):
        scores = [
            RiskOfBiasScore(riskofbias=self, metric=metric)
            for metric in
            RiskOfBiasMetric.get_required_metrics(assessment, study)
        ]
        RiskOfBiasScore.objects.bulk_create(scores)

    def activate(self):
        self.active = True
        self.save()

    def deactivate(self):
        self.active = False
        self.save()

    @property
    def is_complete(self):
        """
        The rich text editor used for notes input adds HTML tags even if input
        is empty, so HTML needs to be stripped out.
        """
        return all([
            len(strip_tags(score.notes)) > 0 for score in self.scores.all()
        ])

    @property
    def study_reviews_complete(self):
        return all([
            rob.is_complete
            for rob in self.study.get_active_robs(with_final=False)
        ])

    @classmethod
    def copy_riskofbias(cls, copy_to_assessment, copy_from_assessment):
        # delete existing study quality metrics and domains
        copy_to_assessment\
            .rob_domains.all()\
            .delete()

        # copy domains and metrics to assessment
        for domain in copy_from_assessment.rob_domains.all():
            metrics = list(domain.metrics.all())  # force evaluation
            domain.id = None
            domain.assessment = copy_to_assessment
            domain.save()
            for metric in metrics:
                metric.id = None
                metric.domain = domain
                metric.save()

    @classmethod
    def delete_caches(cls, ids):
        SerializerHelper.delete_caches(cls, ids)

    @staticmethod
    def flat_complete_header_row():
        return (
            'rob-id',
            'rob-active',
            'rob-final',
            'rob-author_id',
            'rob-author_name'
        )

    @staticmethod
    def flat_complete_data_row(ser):
        return (
            ser['id'],
            ser['active'],
            ser['final'],
            ser['author']['id'],
            ser['author']['full_name']
        )


class RiskOfBiasScore(models.Model):
    RISK_OF_BIAS_SCORE_CHOICES = (
        (10, 'Not reported'),
        (1, 'Definitely high risk of bias'),
        (2, 'Probably high risk of bias'),
        (3, 'Probably low risk of bias'),
        (4, 'Definitely low risk of bias'),
        (0, 'Not applicable'))

    SCORE_SYMBOLS = {
        1: '--',
        2: '-',
        3: '+',
        4: '++',
        0: '-',
        10: 'NR',
    }

    SCORE_SHADES = {
        1: '#CC3333',
        2: '#FFCC00',
        3: '#6FFF00',
        4: '#00CC00',
        0: '#FFCC00',
        10: '#E8E8E8',
    }

    riskofbias = models.ForeignKey(
        RiskOfBias,
        related_name='scores')
    metric = models.ForeignKey(
        RiskOfBiasMetric,
        related_name='scores')
    score = models.PositiveSmallIntegerField(
        choices=RISK_OF_BIAS_SCORE_CHOICES,
        default=10)
    notes = models.TextField(
        blank=True)

    class Meta:
        ordering = ('metric', 'id')

    def __unicode__(self):
        return u'{} {}'.format(self.riskofbias, self.metric)

    def get_assessment(self):
        return self.metric.get_assessment()

    @staticmethod
    def flat_complete_header_row():
        return (
            'rob-domain_id',
            'rob-domain_name',
            'rob-domain_description',
            'rob-metric_id',
            'rob-metric_metric',
            'rob-metric_description',
            'rob-score_id',
            'rob-score_score',
            'rob-score_description',
            'rob-score_notes',
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
            ser['score'],
            ser['score_description'],
            cleanHTML(ser['notes']),
        )

    @classmethod
    def assessment_qs(cls, assessment_id):
        return cls.objects.filter(riskofbias__study__assessment=assessment_id)

    @property
    def score_symbol(self):
        return self.SCORE_SYMBOLS[self.score]

    @property
    def score_shade(self):
        return self.SCORE_SHADES[self.score]

    @classmethod
    def delete_caches(cls, ids):
        id_lists = [(score.riskofbias.id, score.riskofbias.study_id) for score in cls.objects.filter(id__in=ids)]
        rob_ids, study_ids = zip(*id_lists)
        RiskOfBias.delete_caches(rob_ids)
        Study.delete_caches(study_ids)


class RiskOfBiasAssessment(models.Model):
    assessment = models.OneToOneField(
        Assessment,
        related_name='rob_settings')
    number_of_reviewers = models.PositiveSmallIntegerField(
        default=1)

    def get_absolute_url(self):
        return reverse('riskofbias:arob_reviewers', args=[self.assessment.pk])

    @classmethod
    def build_default(cls, assessment):
        RiskOfBiasAssessment.objects.create(assessment=assessment)

    @classmethod
    def assessment_qs(cls, assessment_id):
        return cls.objects.filter(assessment=assessment_id)


reversion.register(RiskOfBiasDomain)
reversion.register(RiskOfBiasMetric)
reversion.register(RiskOfBias)
reversion.register(RiskOfBiasScore)
