# Generated by Django 2.2.15 on 2020-08-28 15:14

import uuid

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models

from hawc.apps.assessment.constants import JobStatus, JobType


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0019_log_blog"),
    ]

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                (
                    "task_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "PENDING"), (2, "SUCCESS"), (3, "FAILURE")],
                        default=JobStatus.PENDING,
                        editable=False,
                    ),
                ),
                (
                    "job",
                    models.PositiveSmallIntegerField(choices=[(1, "TEST")], default=JobType.TEST),
                ),
                (
                    "kwargs",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True, default=dict, null=True
                    ),
                ),
                (
                    "result",
                    django.contrib.postgres.fields.jsonb.JSONField(default=dict, editable=False),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="jobs",
                        to="assessment.Assessment",
                    ),
                ),
            ],
            options={"ordering": ("-created",)},
        ),
    ]
