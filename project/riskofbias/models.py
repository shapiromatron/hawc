import json
import logging
import os
import collections

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

from model_utils import Choices

from reversion import revisions as reversion

from assessment.models import Assessment
from myuser.models import HAWCUser
from lit.models import Reference
from study.models import Study
from utils.helper import cleanHTML, HAWCDjangoJSONEncoder, SerializerHelper
from utils.models import get_crumbs

from . import managers

class RiskOfBiasDomain(models.Model):
    objects = managers.RiskOfBiasDomainManager()

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
    is_overall_confidence = models.BooleanField(
        default = False
        ,verbose_name = "Overall confidence?"
        ,help_text = "Is this domain for overall confidence?"
    )

    class Meta:
        unique_together = ('assessment', 'name')
        ordering = ('pk', )

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.assessment

    @classmethod
    def build_default(cls, assessment):
        """
        Construct default Study Evaluation domains/metrics for an assessment.
        The Study Evaluation domains and metrics are those defined by NTP/OHAT
        protocols for Study Evaluation
        """
        fn = os.path.join(
            settings.PROJECT_PATH,
            'riskofbias/fixtures/iris_study_quality_defaults.json'
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
    def copy_across_assessment(cls, cw, studies, assessment):
        # Copy domain and metrics across studies as well. If a domain and
        # metric have identical names in the new assessment as the old,
        # then don't create new metrics and domains. If the names are not
        # identical, then create a new one. Save metric old:new IDs in a
        # crosswalk which is returned.

        # assert all studies come from a single assessment
        source_assessment = Assessment.objects\
            .filter(references__in=studies)\
            .distinct()
        if source_assessment.count() != 1:
            raise ValueError('Studies must come from the same assessment')
        source_assessment = source_assessment[0]
        cw[Assessment.COPY_NAME][source_assessment.id] = assessment.id

        def get_key(metric):
            return '{}: {}'.format(metric.domain.name, metric.name)

        # create a map of domain + metric for new assessment
        metrics = RiskOfBiasMetric.objects\
            .filter(domain__assessment=assessment)
        metric_mapping = {get_key(metric): metric.id for metric in metrics}

        # if any duplicates exist; create new
        if len(metric_mapping) != metrics.count():
            metric_mapping = {}

        # create a map of existing domains for assessment
        domain_mapping = {
            domain.name: domain.id for domain in
            cls.objects.filter(assessment=assessment)
        }

        # map or create new objects
        for metric in RiskOfBiasMetric.objects\
                .filter(domain__assessment=source_assessment):

            source_metric_id = metric.id
            key = get_key(metric)
            target_metric_id = metric_mapping.get(key)

            # if existing metric doesn't exist, make one
            if target_metric_id is None:

                domain = metric.domain
                # if existing domain doesn't exist, make one
                if domain_mapping.get(domain.name) is None:
                    # domain not found; we must create one
                    domain.id = None
                    domain.assessment_id = assessment.id
                    domain.save()
                    domain_mapping[domain.name] = domain.id
                    logging.info('Created RoB domain: {} -> {}'.
                                 format(domain.name, domain.id))

                metric.id = None
                metric.domain_id = domain_mapping[domain.name]
                metric.save()
                target_metric_id = metric.id
                logging.info('Created RoB metric: {} -> {}'.
                             format(key, target_metric_id))

            cw[RiskOfBiasMetric.COPY_NAME][source_metric_id] = target_metric_id

        return cw


class RiskOfBiasMetric(models.Model):
    objects = managers.RiskOfBiasMetricManager()

    domain = models.ForeignKey(
        RiskOfBiasDomain,
        related_name='metrics')
    name = models.CharField(
        max_length=256)
    short_name = models.CharField(
        max_length=50,
        blank=True)
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
    hide_description = models.BooleanField(
        default=False,
        verbose_name='Hide description?',
        help_text='Hide the description on reports?')
    use_short_name = models.BooleanField(
        default=False,
        verbose_name='Use the short name?',
        help_text='Use the short name in visualizations?')
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

    COPY_NAME = 'metrics'

    class Meta:
        ordering = ('domain', 'id')

    def __str__(self):
        return self.name

    def get_assessment(self):
        return self.domain.get_assessment()

    @classmethod
    def build_metrics_for_one_domain(cls, domain, metrics):
        """
        Build multiple Study Evaluation metrics given a domain django object and a
        list of python dictionaries for each metric.
        """
        objs = []
        for metric in metrics:
            obj = RiskOfBiasMetric(**metric)
            obj.domain = domain
            objs.append(obj)
        RiskOfBiasMetric.objects.bulk_create(objs)

class RiskOfBias(models.Model):
    objects = managers.RiskOfBiasManager()

    study = models.ForeignKey(
        'study.Study',
        related_name='riskofbiases',
        null=True)

    identifiers_id = models.ForeignKey(
        Reference,
        related_name='heroids',
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

    def __str__(self):
        return '{} (Risk of Bias)'.format(self.study.short_citation)

    def get_assessment(self):
        return self.study.get_assessment()

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

    @staticmethod
    def get_qs_json(queryset, json_encode=True):
        robs = [rob.get_json(json_encode=False) for rob in queryset]
        if json_encode:
            return json.dumps(robs, cls=HAWCDjangoJSONEncoder)
        else:
            return robs

    def update_scores(self, assessment):
        """Sync RiskOfBiasScore for this study based on assessment requirements.

        Metrics may change based on study type and metric requirements by study
        type. This method is called via signals when the study type changes,
        or when a metric is altered.  RiskOfBiasScore are created/deleted as
        needed.
        """
        metrics = RiskOfBiasMetric.objects.get_required_metrics(assessment, self.study)\
            .prefetch_related('scores')
        scores = self.scores.all()
        # add any scores that are required and not currently created
        for metric in metrics:
            if not (metric.scores.all() & scores):
                logging.info('Creating score: {}->{}'.format(self.study, metric))
                RiskOfBiasScore.objects.create(riskofbias=self, metric=metric)
        # delete any scores that are no longer required
        for score in scores:
            if score.metric not in metrics:
                logging.info('Deleting score: {}->{}'.format(self.study, score.metric))
                score.delete()

    def build_scores(self, assessment, study):
        scores = [
            RiskOfBiasScore(riskofbias=self, metric=metric)
            for metric in
            RiskOfBiasMetric.objects.get_required_metrics(assessment, study)
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
            len(strip_tags(score.notes)) > 0 for score in self.scores.all() if score.score is not 0
        ])

    @property
    def study_reviews_complete(self):
        return all([
            rob.is_complete
            for rob in self.study.get_active_robs(with_final=False)
        ])

    @staticmethod
    def copy_riskofbias(copy_to_assessment, copy_from_assessment):
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

    @classmethod
    def copy_across_assessment(cls, cw, studies, assessment):
        # Copy active, final, Study Evaluation assessments for each study, and
        # assign to project manager selected at random. Requires that for all
        # studies, a crosswalk exists which assigns a new RiskOfBiasMetric ID
        # from the old RiskOfBiasMetric ID.

        author = assessment.project_manager.first()
        final_robs = cls.objects.filter(study__in=studies, active=True, final=True)

        # copy reviews and scores
        for rob in final_robs:
            scores = list(rob.scores.all())

            rob.id = None
            rob.study_id = cw[Study.COPY_NAME][rob.study_id]
            rob.author = author
            rob.save()

            for score in scores:
                score.id = None
                score.riskofbias_id = rob.id
                score.metric_id = cw[RiskOfBiasMetric.COPY_NAME][score.metric_id]
                score.save()

        return cw


class RiskOfBiasMetricAnswers(models.Model):
    metric = models.ForeignKey(
        RiskOfBiasMetric,
        related_name='answers',
        null=True,
        blank=True)
    answer_choice = models.TextField(
        default = 'Not reported',
        blank=False,
        unique=True
    )
    answer_symbol = models.TextField(
        default = 'NR',
        blank=False,
        unique=True
    )
    answer_score = models.PositiveSmallIntegerField(
        default = 10,
        unique=True
    )
    answer_shade = models.CharField(
        max_length=7,
        default = '#FFCC00'
    )
    answer_order = models.IntegerField(
        default = 1,
        unique=True
    )
    class Meta:
        verbose_name_plural = "Study Evaluation metric answers"
        ordering = ('metric', 'answer_order')

    def get_assessment(self):
        return self.metric.domain.get_assessment()

class RiskOfBiasAnswersRecorded(models.Model):
    riskofbias = models.ForeignKey(
        RiskOfBias,
        related_name='answers_recorded'
    )
    answers = models.ForeignKey(
        RiskOfBiasMetricAnswers,
        related_name='answers_recorded'
    )
    recorded_score = models.PositiveSmallIntegerField(
        default = 10
    )
    recorded_notes = models.TextField(
        blank=True
    )
    created = models.DateTimeField(
        auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True)

class RiskOfBiasScore(models.Model):
    objects = managers.RiskOfBiasScoreManager()

    RISK_OF_BIAS_SCORE_CHOICES = (
        (10, 'Not reported'),
        (1, 'Critically deficient'),
        (2, 'Poor'),
        (3, 'Adequate'),
        (4, 'Good'),
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
        10: '#FFCC00',
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

    def __str__(self):
        return '{} {}'.format(self.riskofbias, self.metric)

    def get_assessment(self):
        return self.metric.get_assessment()

    @staticmethod
    def flat_complete_header_row():
        return (
            'rob-domain_id',
            'rob-domain_name',
            'rob-domain_description',
            'rob-metric_id',
            'rob-metric_name',
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
            ser['metric']['name'],
            ser['metric']['description'],
            ser['id'],
            ser['score'],
            ser['score_description'],
            cleanHTML(ser['notes']),
        )

    @property
    def score_symbol(self):
        return self.SCORE_SYMBOLS[self.score]

    @property
    def score_shade(self):
        return self.SCORE_SHADES[self.score]

    @classmethod
    def delete_caches(cls, ids):
        id_lists = [(score.riskofbias.id, score.riskofbias.study_id) for score in cls.objects.filter(id__in=ids)]
        rob_ids, study_ids = list(zip(*id_lists))
        RiskOfBias.delete_caches(rob_ids)
        Study.delete_caches(study_ids)


class RiskOfBiasAssessment(models.Model):
    objects = managers.RiskOfBiasAssessmentManager()

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


reversion.register(RiskOfBiasDomain)
reversion.register(RiskOfBiasMetric)
reversion.register(RiskOfBias)
reversion.register(RiskOfBiasScore)
