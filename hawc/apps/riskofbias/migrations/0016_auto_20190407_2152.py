# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-08 02:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riskofbias", "0015_riskofbiasassessment_help_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="riskofbiasdomain",
            name="is_overall_confidence",
            field=models.BooleanField(
                default=False,
                help_text="Is this domain for overall confidence?",
                verbose_name="Overall confidence?",
            ),
        ),
        migrations.AddField(
            model_name="riskofbiasmetric",
            name="hide_description",
            field=models.BooleanField(
                default=False,
                help_text="Hide the description on reports?",
                verbose_name="Hide description?",
            ),
        ),
        migrations.AddField(
            model_name="riskofbiasmetric",
            name="required_invitro",
            field=models.BooleanField(
                default=True,
                help_text="Is this metric required for in-vitro studies?<br/><b>CAUTION:</b> Removing requirement will destroy all in-vitro responses previously entered for this metric.",
                verbose_name="Required for in-vitro?",
            ),
        ),
        migrations.AddField(
            model_name="riskofbiasmetric",
            name="short_name",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="riskofbiasmetric",
            name="use_short_name",
            field=models.BooleanField(
                default=False,
                help_text="Use the short name in visualizations?",
                verbose_name="Use the short name?",
            ),
        ),
        migrations.AlterField(
            model_name="riskofbiasdomain",
            name="description",
            field=models.TextField(blank=True),
        ),
    ]
