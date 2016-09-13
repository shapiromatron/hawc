from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from study.models import Study

from . import managers


class Task(models.Model):

    TYPE_PREPARATION = 10
    TYPE_EXTRACTION = 20
    TYPE_QA = 30
    TYPE_ROB = 40
    TYPE_CHOICES = (
        (TYPE_PREPARATION, 'preparation'),
        (TYPE_EXTRACTION, 'extraction'),
        (TYPE_QA, 'qa/qc'),
        (TYPE_ROB, 'rob completed'),
    )

    STATUS_NOT_STARTED = 10
    STATUS_STARTED = 20
    STATUS_COMPLETED = 30
    STATUS_ABANDONED = 40
    STATUS_CHOICES = (
        (STATUS_NOT_STARTED, 'not started'),
        (STATUS_STARTED, 'started'),
        (STATUS_COMPLETED, 'completed'),
        (STATUS_ABANDONED, 'abandoned'),
    )

    objects = managers.TaskManager()

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name='tasks')
    study = models.ForeignKey(
        Study,
        related_name='tasks')
    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES)
    status = models.PositiveSmallIntegerField(
        default=STATUS_CHOICES[0][0],
        choices=STATUS_CHOICES)
    open = models.BooleanField(
        default=False)
    due_date = models.DateTimeField(
        blank=True,
        null=True)
    started = models.DateTimeField(
        blank=True,
        null=True)
    completed = models.DateTimeField(
        blank=True,
        null=True)

    class Meta:
        unique_together = (('study', 'type'), )
        ordering = ('study', 'type', )

    def __unicode__(self):
        return u'{}: {}'.format(self.study, self.get_type_display())

    @classmethod
    def dashboard_metrics(cls, qs):
        return {
            'studies': qs.order_by('study_id').distinct('study_id').count(),
            'tasks': qs.count()
        }
