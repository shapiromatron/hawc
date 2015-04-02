# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0012_auto_20141104_1506'),
    ]

    operations = [

        migrations.RemoveField(
            model_name='ivendpointgroup',
            name='cytotoxicity_observed',
        ),

        migrations.AddField(
            model_name='ivcelltype',
            name='strain',
            field=models.CharField(default=b'not applicable', max_length=64),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ivchemical',
            name='precipitation',
            field=models.PositiveSmallIntegerField(default=0, help_text=b'Was precipitation observed?', verbose_name=b'Precipitation', choices=[(0, b'not reported'), (1, b'no'), (2, b'yes')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ivendpoint',
            name='effect',
            field=models.CharField(default='', help_text=b'Effect, using common-vocabulary', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ivendpoint',
            name='trend_test_notes',
            field=models.CharField(help_text=b'Notes describing details on the trend-test performed', max_length=256, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ivendpointgroup',
            name='cytotoxicity_observed',
            field=models.NullBooleanField(default=None, choices=[(None, b'not reported'), (False, b'not observed'), (True, b'observed')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ivendpointgroup',
            name='precipitation_observed',
            field=models.NullBooleanField(default=None, choices=[(None, b'not reported'), (False, b'not observed'), (True, b'observed')]),
            preserve_default=True,
        ),

        migrations.AlterField(
            model_name='ivchemical',
            name='cas_notes',
            field=models.CharField(max_length=256, verbose_name=b'CAS determination notes'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ivchemical',
            name='purity',
            field=models.CharField(help_text=b'Ex: >99%, not-reported, etc.', max_length=32, verbose_name=b'Chemical purity'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ivexperiment',
            name='control_notes',
            field=models.CharField(help_text=b'Additional details related to controls', max_length=256, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ivendpoint',
            name='category',
            field=models.ForeignKey(related_name='endpoints', blank=True, to='invitro.IVEndpointCategory', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ivendpoint',
            name='overall_pattern',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'not-available'), (1, b'increase'), (2, b'increase, then decrease'), (6, b'increase, then no change'), (3, b'decrease'), (4, b'decrease, then increase'), (7, b'decrease, then no change'), (5, b'no clear pattern')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ivendpoint',
            name='short_description',
            field=models.CharField(help_text=b'Short (<128 character) description of effect & measurement', max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ivbenchmark',
            name='value',
            field=models.FloatField(),
            preserve_default=True,
        ),

    ]
