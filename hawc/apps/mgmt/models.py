import json
import logging

from django.conf import settings
from django.db import models
from django.utils import timezone

from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper
from ..study.models import Study
from . import managers


class Task(models.Model):

    TYPE_PREPARATION = 10
    TYPE_EXTRACTION = 20
    TYPE_QA = 30
    TYPE_ROB = 40
    TYPE_CHOICES = (
        (TYPE_PREPARATION, "preparation"),
        (TYPE_EXTRACTION, "extraction"),
        (TYPE_QA, "qa/qc"),
        (TYPE_ROB, "rob completed"),
    )

    STATUS_NOT_STARTED = 10
    STATUS_STARTED = 20
    STATUS_COMPLETED = 30
    STATUS_ABANDONED = 40
    STATUS_CHOICES = (
        (STATUS_NOT_STARTED, "not started"),
        (STATUS_STARTED, "started"),
        (STATUS_COMPLETED, "completed"),
        (STATUS_ABANDONED, "abandoned"),
    )

    objects = managers.TaskManager()

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="tasks")
    study = models.ForeignKey(Study, related_name="tasks")
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    status = models.PositiveSmallIntegerField(default=STATUS_CHOICES[0][0], choices=STATUS_CHOICES)
    open = models.BooleanField(default=False)
    due_date = models.DateTimeField(blank=True, null=True)
    started = models.DateTimeField(blank=True, null=True)
    completed = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = (("study", "type"),)
        ordering = (
            "study",
            "type",
        )

    def __str__(self):
        return f"{self.study}: {self.get_type_display()}"

    @classmethod
    def dashboard_metrics(cls, qs):
        return dict(studies=qs.order_by("study_id").distinct("study_id").count(), tasks=qs.count(),)

    def get_assessment(self):
        return self.study.get_assessment()

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    @staticmethod
    def get_qs_json(queryset, json_encode=True):
        tasks = [task.get_json(json_encode=False) for task in queryset]
        if json_encode:
            return json.dumps(tasks, cls=HAWCDjangoJSONEncoder)
        else:
            return tasks

    def save(self, *args, **kwargs):
        """Alter model business logic for timestamps and open/closed."""
        if self.status == self.STATUS_NOT_STARTED:
            self.started = None
            self.completed = None
            self.open = False
        elif self.status == self.STATUS_STARTED:
            self.started = timezone.now()
            self.completed = None
            self.open = True
        elif self.status in [self.STATUS_COMPLETED, self.STATUS_ABANDONED]:
            self.completed = timezone.now()
            self.open = False

        super().save(*args, **kwargs)

    def start_if_unstarted(self, user):
        """Save task as started by user if currently not started."""
        if self.status == self.STATUS_NOT_STARTED:
            logging.info(f'Starting "{self.get_type_display()}" task {self.id}')
            self.owner = user
            self.status = self.STATUS_STARTED
            self.save()

    def stop_if_started(self):
        """Stop task if currently started."""
        if self.status == self.STATUS_STARTED:
            logging.info(f'Stopping "{self.get_type_display()}" task {self.id}')
            self.status = self.STATUS_COMPLETED
            self.save()
