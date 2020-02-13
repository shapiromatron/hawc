# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-13 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("riskofbias", "0019_auto_20190823_2345"),
    ]

    operations = [
        migrations.CreateModel(
            name="RiskOfBiasScoreOverrideObject",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="contenttypes.ContentType"
                    ),
                ),
                (
                    "score",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="overriden_objects",
                        to="riskofbias.RiskOfBiasScore",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="riskofbiasscore",
            name="is_default",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="riskofbiasscore",
            name="label",
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
