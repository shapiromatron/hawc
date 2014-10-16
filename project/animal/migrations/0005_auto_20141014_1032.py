# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0004_auto_20141010_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='dosingregime',
            name='duration_exposure',
            field=models.FloatField(help_text=b'Length of exposure period, in days (fractions allowed)', null=True, verbose_name=b'Exposure duration (days)', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dosingregime',
            name='duration_observation',
            field=models.FloatField(help_text=b'Length of observation period, in days (fractions allowed)', null=True, verbose_name=b'Observation duration (days)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='purity',
            field=models.FloatField(blank=True, help_text=b'Assumed to be greater-than numeric-value specified (ex: > 95.5%)', null=True, verbose_name=b'Chemical purity (%)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
