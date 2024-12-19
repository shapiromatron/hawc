# Generated by Django 5.1.1 on 2024-10-22 21:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0032_experiment_guideline"),
        ("vocab", "0010_load_guidelineprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="Observation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("tested_status", models.BooleanField(default=False)),
                ("reported_status", models.BooleanField(default=False)),
                (
                    "endpoint",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vocab.term",
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="animal.experiment",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("id",),
            },
        ),
    ]
