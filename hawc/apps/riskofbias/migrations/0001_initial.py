# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-07 15:10


import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("assessment", "0006_auto_20150724_1151"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("study", "0004_auto_20160407_1010"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    state_operations = [
        migrations.CreateModel(
            name="RiskOfBias",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "score",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Definitely high risk of bias"),
                            (2, "Probably high risk of bias"),
                            (3, "Probably low risk of bias"),
                            (4, "Definitely low risk of bias"),
                            (0, "Not applicable"),
                        ],
                        default=4,
                    ),
                ),
                ("notes", models.TextField(blank=True, default="")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="riskofbiases",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
            options={
                "ordering": ("content_type", "object_id", "metric"),
                "verbose_name_plural": "Study Qualities",
            },
        ),
        migrations.CreateModel(
            name="RiskOfBiasDomain",
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
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField(default="")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sq_domains",
                        to="assessment.Assessment",
                    ),
                ),
            ],
            options={"ordering": ("pk",)},
        ),
        migrations.CreateModel(
            name="RiskOfBiasMetric",
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
                ("metric", models.CharField(max_length=256)),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="HTML text describing scoring of this field.",
                    ),
                ),
                (
                    "required_animal",
                    models.BooleanField(
                        default=True,
                        help_text="Is this metric required for animal bioassay studies?",
                        verbose_name="Required for bioassay?",
                    ),
                ),
                (
                    "required_epi",
                    models.BooleanField(
                        default=True,
                        help_text="Is this metric required for human epidemiological studies?",
                        verbose_name="Required for epidemiology?",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "domain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="metrics",
                        to="riskofbias.RiskOfBiasDomain",
                    ),
                ),
            ],
            options={"ordering": ("domain", "id")},
        ),
        migrations.AddField(
            model_name="riskofbias",
            name="metric",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="qualities",
                to="riskofbias.RiskOfBiasMetric",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="riskofbiasdomain",
            unique_together=set([("assessment", "name")]),
        ),
        migrations.AlterUniqueTogether(
            name="riskofbias",
            unique_together=set([("content_type", "object_id", "metric")]),
        ),
    ]

    operations = [migrations.SeparateDatabaseAndState(state_operations=state_operations)]
