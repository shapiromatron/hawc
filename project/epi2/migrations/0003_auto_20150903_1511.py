# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0002_auto_20150828_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='outcome',
            name='system',
            field=models.CharField(help_text=b'Relevant biological system', max_length=128, blank=True),
        ),
        migrations.AlterField(
            model_name='outcome',
            name='diagnostic',
            field=models.PositiveSmallIntegerField(choices=[(0, b'not reported'), (1, b'medical professional or test'), (2, b'medical records'), (3, b'self-reported'), (4, b'questionnaire')]),
        ),
        migrations.AlterField(
            model_name='result',
            name='estimate_type',
            field=models.PositiveSmallIntegerField(default=0, verbose_name=b'Central estimate type', choices=[(0, None), (1, b'mean'), (2, b'geometric mean'), (3, b'median'), (5, b'point'), (4, b'other')]),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='design',
            field=models.CharField(max_length=2, choices=[(b'CO', b'Cohort'), (b'CC', b'Case control'), (b'NC', b'Nested case control'), (b'CR', b'Case report'), (b'SE', b'Case series'), (b'CT', b'Controlled trial'), (b'CS', b'Cross sectional')]),
        ),
    ]
