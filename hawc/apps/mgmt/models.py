import json
import logging
from collections import Counter
from typing import Self

import plotly.express as px
from django.conf import settings
from django.db import models
from django.utils import timezone
from plotly.graph_objs._figure import Figure

from ..common.helper import HAWCDjangoJSONEncoder, SerializerHelper
from ..study.models import Study
from . import constants, managers

logger = logging.getLogger(__name__)


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
    type = models.PositiveSmallIntegerField(choices=constants.TaskType)
    status = models.PositiveSmallIntegerField(
        default=constants.TaskStatus.NOT_STARTED, choices=constants.TaskStatus
    )
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
        if self.status == constants.TaskStatus.NOT_STARTED:
            self.started = None
            self.completed = None
            self.open = False
        elif self.status == constants.TaskStatus.STARTED:
            self.started = timezone.now()
            self.completed = None
            self.open = True
        elif self.status in [
            constants.TaskStatus.COMPLETED,
            constants.TaskStatus.ABANDONED,
        ]:
            self.completed = timezone.now()
            self.open = False

        super().save(*args, **kwargs)

    def start_if_unstarted(self, user):
        """Save task as started by user if currently not started."""
        if self.status == constants.TaskStatus.NOT_STARTED:
            logger.info(f'Starting "{self.get_type_display()}" task {self.id}')
            self.owner = user
            self.status = constants.TaskStatus.STARTED
            self.save()

    def stop_if_started(self):
        """Stop task if currently started."""
        if self.status == constants.TaskStatus.STARTED:
            logger.info(f'Stopping "{self.get_type_display()}" task {self.id}')
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
