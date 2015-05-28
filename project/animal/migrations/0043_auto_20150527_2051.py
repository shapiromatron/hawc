# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0042_dosingregime_duration_exposure_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpointgroup',
            name='n',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
    ]
