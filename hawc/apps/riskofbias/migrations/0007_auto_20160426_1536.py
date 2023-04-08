# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-26 20:36


import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def createRoBAssessment(apps, schema_editor):
    Assessment = apps.get_model("assessment", "Assessment")
    RoBAssessment = apps.get_model("riskofbias", "RiskOfBiasAssessment")
    for assessment in Assessment.objects.all():
        RoBAssessment.objects.create(assessment=assessment)


def setDefaultRoBAuthor(apps, schema_editor):
    RiskOfBias = apps.get_model("riskofbias", "RiskOfBias")
    for rob in RiskOfBias.objects.all():
        rob.conflict_resolution = True
        rob.author = rob.study.assessment.project_manager.first()
        rob.save()


def runMigration(apps, schema_editor):
    createRoBAssessment(apps, schema_editor)
    setDefaultRoBAuthor(apps, schema_editor)


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0007_auto_20160426_1124"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("study", "0004_auto_20160407_1010"),
        ("riskofbias", "0006_auto_20160415_1020"),
    ]

    operations = [
        migrations.CreateModel(
            name="RiskOfBiasAssessment",
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
                ("number_of_reviewers", models.PositiveSmallIntegerField(default=1)),
                (
                    "assessment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rob_settings",
                        to="assessment.Assessment",
                    ),
                ),
            ],
        ),
        migrations.RunPython(
            runMigration,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
