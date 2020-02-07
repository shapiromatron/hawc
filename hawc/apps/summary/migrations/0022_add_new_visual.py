# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-29 04:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0021_data_pivot_settings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visual",
            name="visual_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "animal bioassay endpoint aggregation"),
                    (1, "animal bioassay endpoint crossview"),
                    (2, "risk of bias heatmap"),
                    (3, "risk of bias barchart"),
                    (4, "literature tagtree"),
                ]
            ),
        ),
    ]
