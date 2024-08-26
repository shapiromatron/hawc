import json
import logging
from collections import Counter
from typing import Self

import plotly.express as px
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from plotly.graph_objs._figure import Figure

from ..assessment.models import Assessment
from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper
from ..study.models import Study
from . import constants, managers

logger = logging.getLogger(__name__)


# these are assessment specific. Right now there are 4 hard coded task types, we would want to
# create a django migration that converts the hard coded ones into rows in the TaskTable model
# {eg., Preparation, Data Extraction, QA/QC, Study Evaluation}
class TaskType(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    order = models.PositiveSmallIntegerField(help_text="Task order in an assessment")
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


# again, these are currently hard coded, but we'd want to create a django migration that convert the hard coded ones into ones w/ a migration
# current values are {eg., Started, Not Started, Completed, Abandoned}
class TaskStatus(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    value = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(help_text="Status order in assessment")
    color = models.CharField(max_length=7, help_text="Hexadecimal color code")
    terminal_status = models.BooleanField(
        default=False,
        help_text='If a study has this status, should it be considered "finished" for this task type. For example, completed/abandoned would be terminal, while started/ongoing would not be.',
    )
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


# the `TaskTrigger` is basically triggers that would say something like if a Study is edited, change this status.
# There can be multiple triggers with the same task type/current status. task triggers an also create tasks
# if current_status is null. These will be implemented as checks in django signals
class TaskTrigger(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)  # is this actually needed
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    current_status = models.ForeignKey(
        TaskStatus, on_delete=models.CASCADE, null=True, related_name="current_triggers"
    )
    next_status = models.ForeignKey(
        TaskStatus, on_delete=models.CASCADE, related_name="next_triggers"
    )
    event = models.PositiveSmallIntegerField(choices=constants.StartTaskTriggerEvent)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class Task(models.Model):
    objects = managers.TaskManager()

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="tasks",
    )
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="tasks")
    type = models.ForeignKey(TaskType, on_delete=models.CASCADE, blank=True, null=True)
    status = models.ForeignKey(TaskStatus, on_delete=models.CASCADE, blank=True, null=True)
    notes = models.TextField(default="", help_text="User notes on status")
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
        return f"{self.study}: {self.type.name}"

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
        """Alter model business logic for timestamps and completion"""
        if self.status.terminal_status:
            self.completed = timezone.now()
        else:
            self.completed = None

        super().save(*args, **kwargs)

    def start_if_unstarted(self, user):
        """Save task as started by user if currently not started."""
        if not self.started:
            self.owner = user
            logger.info(f'Starting "{self.type.name()}" task {self.id}')
        self.save()

    def stop_if_started(self):
        """Stop task if currently started."""
        if self.started:
            logger.info(f'Stopping "{self.type.name}" task {self.id}')
            self.status = constants.TaskStatus.COMPLETED
            self.save()

    @classmethod
    def barchart(cls, tasks: list[Self], title: str = "") -> Figure:
        counts = Counter(el.status for el in tasks)
        status_count = {
            label: counts.get(value, 0) for value, label in constants.TaskStatus.choices
        }
        plot = px.bar(
            x=list(status_count.values()),
            y=list(status_count.keys()),
            orientation="h",
            title=title,
            width=500,
            height=200,
            template="none",
            color=list(status_count.keys()),
            color_discrete_sequence=["#CFCFCF", "#FFCC00", "#00CC00", "#CC3333"],
            text_auto=True,
        )
        plot.update_layout(
            xaxis={"title": "Tasks"},
            yaxis={"title": "", "autorange": "reversed"},
            margin={"l": 85, "r": 0, "t": 30, "b": 30},
            showlegend=False,
            hovermode=False,
        )
        return plot

    @property
    def overdue(self):
        return (
            self.due_date
            and self.status in [constants.TaskStatus.NOT_STARTED, constants.TaskStatus.STARTED]
            and self.due_date < now()
        )
