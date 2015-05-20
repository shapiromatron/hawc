# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0009_auto_20150424_1031'),
        ('summary', '0008_auto_20150519_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='visual',
            name='studies',
            field=models.ManyToManyField(help_text=b'Studies to be included in visualization', related_name='visuals', null=True, to='study.Study', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='visual',
            name='visual_type',
            field=models.PositiveSmallIntegerField(choices=[(0, b'animal bioassay endpoint aggregation'), (1, b'animal bioassay endpoint crossview'), (2, b'risk of bias heatmap'), (3, b'risk of bias barchart')]),
            preserve_default=True,
        ),
    ]
