# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0002_auto_20150923_0951'),
    ]

    operations = [
        migrations.AddField(
            model_name='exposure2',
            name='measured',
            field=models.CharField(max_length=128, verbose_name=b'What was measured', blank=True),
        ),
        migrations.AddField(
            model_name='result',
            name='trend_test',
            field=models.CharField(max_length=128, blank=True),
        ),
        migrations.AddField(
            model_name='studypopulation',
            name='age_profile',
            field=models.CharField(help_text=b'Age profile of population (ex: adults, children, pregnant women, etc.)', max_length=128, blank=True),
        ),
        migrations.AddField(
            model_name='studypopulation',
            name='source',
            field=models.CharField(help_text=b'Population source (ex: general population, environmental exposure, occupational cohort)', max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='exposure2',
            name='metric',
            field=models.CharField(max_length=128, verbose_name=b'Measurement Metric'),
        ),
        migrations.AlterField(
            model_name='exposure2',
            name='name',
            field=models.CharField(help_text=b'Name of exposure and exposure-route', max_length=128),
        ),
    ]
