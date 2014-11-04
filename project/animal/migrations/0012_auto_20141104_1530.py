# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0011_remove_animalgroup_dose_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='endpoint',
            name='observation_time',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='endpoint',
            name='observation_time_units',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'not-reported'), (1, b'seconds'), (2, b'minutes'), (3, b'hours'), (4, b'days'), (5, b'weeks'), (6, b'months')]),
            preserve_default=True,
        ),
    ]
