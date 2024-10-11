# Generated by Django 5.1.1 on 2024-10-11 14:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vocab", "0008_alter_term_namespace"),
    ]

    operations = [
        migrations.CreateModel(
            name="GuidelineProfile",
            fields=[
                (
                    "guideline_profile_id",
                    models.PositiveIntegerField(
                        primary_key=True, serialize=False, unique=True, verbose_name="ID"
                    ),
                ),
                ("guideline_id", models.PositiveIntegerField()),
                (
                    "endpoint",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vocab.term",
                    ),
                ),
                ("endpoint_category", models.CharField(max_length=256)),
                ("endpoint_type", models.CharField(max_length=256)),
                ("endpoint_target", models.CharField(max_length=256)),
                (
                    "obs_status",
                    models.CharField(
                        choices=[
                            ("NM", "NM"),
                            ("not required", "not required"),
                            ("recommended", "recommended"),
                            ("required", "required"),
                            ("triggered", "triggered"),
                        ],
                        null=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "ordering": ("guideline_profile_id",),
            },
        ),
    ]
