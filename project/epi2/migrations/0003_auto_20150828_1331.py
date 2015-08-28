# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0002_auto_20150824_1444'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exposure2',
            options={'ordering': ('name',), 'verbose_name': 'Exposure', 'verbose_name_plural': 'Exposures'},
        ),
        migrations.RemoveField(
            model_name='groupcollection',
            name='outcomes',
        ),
        migrations.AlterField(
            model_name='group',
            name='sex',
            field=models.CharField(default=b'U', max_length=1, choices=[(b'U', b'Not reported'), (b'M', b'Male'), (b'F', b'Female'), (b'B', b'Male and Female')]),
        ),
        migrations.AlterField(
            model_name='groupcollection',
            name='exposure',
            field=models.ForeignKey(related_name='groups', blank=True, to='epi2.Exposure2', help_text=b'Exposure-group associated with this group', null=True),
        ),
        migrations.AlterField(
            model_name='resultadjustmentfactor',
            name='adjustment_factor',
            field=models.ForeignKey(related_name='resfactors', to='epi2.AdjustmentFactor'),
        ),
        migrations.AlterField(
            model_name='resultadjustmentfactor',
            name='result_measurement',
            field=models.ForeignKey(related_name='resfactors', to='epi2.ResultMeasurement'),
        ),
        migrations.AlterField(
            model_name='resultmeasurement',
            name='adjustment_factors',
            field=models.ManyToManyField(related_name='outcomes', through='epi2.ResultAdjustmentFactor', to='epi2.AdjustmentFactor', blank=True),
        ),
    ]
