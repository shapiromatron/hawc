# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-13 22:36
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import riskofbias.models


def migrate_scores(apps, schema_editor):
    RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")
    if settings.HAWC_FLAVOR == "PRIME":
        RiskOfBiasScore.objects.filter(score=0).update(score=10)
        RiskOfBiasScore.objects.filter(score=10).update(score=12)
        RiskOfBiasScore.objects.filter(score=1).update(score=14)
        RiskOfBiasScore.objects.filter(score=2).update(score=15)
        RiskOfBiasScore.objects.filter(score=3).update(score=16)
        RiskOfBiasScore.objects.filter(score=4).update(score=17)
    elif settings.HAWC_FLAVOR == "EPA":
        RiskOfBiasScore.objects.filter(score=0).update(score=20)
        RiskOfBiasScore.objects.filter(score=10).update(score=22)
        RiskOfBiasScore.objects.filter(score=1).update(score=24)
        RiskOfBiasScore.objects.filter(score=2).update(score=25)
        RiskOfBiasScore.objects.filter(score=3).update(score=26)
        RiskOfBiasScore.objects.filter(score=4).update(score=27)
    else:
        raise ValueError("Unknown HAWC flavor")


class Migration(migrations.Migration):

    dependencies = [
        ("riskofbias", "0016_auto_20190407_2152"),
    ]

    operations = [
        migrations.AddField(
            model_name="riskofbiasassessment",
            name="default_questions",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "OHAT"), (2, "EPA")],
                default=riskofbias.models.RiskOfBiasAssessment.get_default_default_questions,
                help_text="If no questions exist, which default questions should be used? If questions already exist, changing this will have no impact.",
                verbose_name="Default questions",
            ),
        ),
        migrations.AddField(
            model_name="riskofbiasassessment",
            name="responses",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "OHAT"), (1, "EPA")],
                default=riskofbias.models.RiskOfBiasAssessment.get_default_responses,
                help_text="Why responses should be used to answering questions:",
                verbose_name="Question responses",
            ),
        ),
        migrations.AlterField(
            model_name="riskofbiasscore",
            name="score",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Not applicable"),
                    (2, "Not reported"),
                    (14, "Definitely high risk of bias"),
                    (15, "Probably high risk of bias"),
                    (16, "Probably low risk of bias"),
                    (17, "Definitely low risk of bias"),
                    (24, "Critically deficient"),
                    (25, "Deficient"),
                    (26, "Adequate"),
                    (27, "Good"),
                ],
                default=10,
            ),
        ),
        migrations.RunPython(migrate_scores),
    ]
