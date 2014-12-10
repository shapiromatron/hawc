# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0014_auto_20141201_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpointgroup',
            name='significance_level',
            field=models.FloatField(default=None, null=True, verbose_name=b'Statistical significance level', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
            preserve_default=True,
        ),
    ]
