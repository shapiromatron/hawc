# Generated by Django 1.9.9 on 2016-09-13 15:00


import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("study", "0008_delete_study_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (10, "preparation"),
                            (20, "extraction"),
                            (30, "qa/qc"),
                            (40, "rob completed"),
                        ]
                    ),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (10, "not started"),
                            (20, "started"),
                            (30, "completed"),
                            (40, "abandoned"),
                        ],
                        default=10,
                    ),
                ),
                ("open", models.BooleanField(default=False)),
                ("due_date", models.DateTimeField(blank=True, null=True)),
                ("started", models.DateTimeField(blank=True, null=True)),
                ("completed", models.DateTimeField(blank=True, null=True)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        related_name="tasks",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        related_name="tasks",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="study.Study",
                    ),
                ),
            ],
            options={"ordering": ("study", "type")},
        ),
        migrations.AlterUniqueTogether(
            name="task",
            unique_together=set([("study", "type")]),
        ),
    ]
