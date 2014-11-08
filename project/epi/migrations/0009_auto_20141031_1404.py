# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0008_metaresult_data_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='metaresult',
            name='ci_units',
            field=models.FloatField(default=0.95, help_text=b'A 95% CI is written as 0.95.', null=True, verbose_name=b'Confidence Interval (CI)', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='singleresult',
            name='ci_units',
            field=models.FloatField(default=0.95, help_text=b'A 95% CI is written as 0.95.', null=True, verbose_name=b'Confidence Interval (CI)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessedoutcomegroup',
            name='ci_units',
            field=models.FloatField(default=0.95, help_text=b'A 95% CI is written as 0.95.', null=True, verbose_name=b'Confidence Interval (CI)', blank=True),
        ),
        migrations.AlterField(
            model_name='metaresult',
            name='lower_ci',
            field=models.FloatField(help_text=b'Numerical value for lower-confidence interval', verbose_name=b'Lower CI'),
        ),
        migrations.AlterField(
            model_name='metaresult',
            name='upper_ci',
            field=models.FloatField(help_text=b'Numerical value for upper-confidence interval', verbose_name=b'Upper CI'),
        ),
        migrations.AlterField(
            model_name='singleresult',
            name='lower_ci',
            field=models.FloatField(help_text=b'Numerical value for lower-confidence interval', null=True, verbose_name=b'Lower CI', blank=True),
        ),
        migrations.AlterField(
            model_name='singleresult',
            name='upper_ci',
            field=models.FloatField(help_text=b'Numerical value for upper-confidence interval', null=True, verbose_name=b'Upper CI', blank=True),
        ),
    ]
