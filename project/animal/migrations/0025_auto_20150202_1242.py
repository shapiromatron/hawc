# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0024_auto_20141218_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='endpoint',
            name='confidence_interval',
            field=models.FloatField(help_text=b'A 95% CI is written as 0.95.', null=True, verbose_name=b'Confidence interval (CI)', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='endpointgroup',
            name='lower_ci',
            field=models.FloatField(help_text=b'Numerical value for lower-confidence interval', null=True, verbose_name=b'Lower CI', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='endpointgroup',
            name='upper_ci',
            field=models.FloatField(help_text=b'Numerical value for upper-confidence interval', null=True, verbose_name=b'Upper CI', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='data_type',
            field=models.CharField(default=b'D', max_length=2, verbose_name=b'Dataset type', choices=[(b'C', b'Continuous'), (b'D', b'Dichotomous'), (b'P', b'Percent Difference'), (b'DC', b'Dichotomous Cancer'), (b'NR', b'Not reported')]),
            preserve_default=True,
        ),
    ]
