# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-08-24 04:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("riskofbias", "0018_auto_20190416_2035"),
    ]

    operations = [
        migrations.AlterField(
            model_name="riskofbiasscore",
            name="score",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (10, "Not applicable"),
                    (12, "Not reported"),
                    (14, "Definitely high risk of bias"),
                    (15, "Probably high risk of bias"),
                    (16, "Probably low risk of bias"),
                    (17, "Definitely low risk of bias"),
                    (20, "Not applicable"),
                    (22, "Not reported"),
                    (24, "Critically deficient"),
                    (25, "Deficient"),
                    (26, "Adequate"),
                    (27, "Good"),
                ],
                default=999,
            ),
        ),
    ]
