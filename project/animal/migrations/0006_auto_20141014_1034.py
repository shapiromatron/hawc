# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0005_auto_20141014_1032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dosingregime',
            name='duration_observation',
        ),
        migrations.AddField(
            model_name='animalgroup',
            name='duration_observation',
            field=models.FloatField(help_text=b'Length of observation period, in days (fractions allowed)', null=True, verbose_name=b'Observation duration (days)', blank=True),
            preserve_default=True,
        ),
    ]
