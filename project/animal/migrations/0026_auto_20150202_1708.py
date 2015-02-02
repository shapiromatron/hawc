# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0025_auto_20150202_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='endpoint',
            name='power_notes',
            field=models.TextField(help_text=b'Power of study-design to detect change from control', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='statistical_test',
            field=models.CharField(help_text=b'Description of statistical analysis techniques used', max_length=256, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='trend_value',
            field=models.FloatField(help_text=b'Numerical result for trend-test, if available', null=True, blank=True),
            preserve_default=True,
        ),
    ]
