# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0009_auto_20150723_1523'),
        ('assessment', '0004_auto_20150723_1530')
    ]

    state_operations = [
        migrations.AlterField(
            model_name='animalgroup',
            name='species',
            field=models.ForeignKey(to='assessment.Species'),
        ),
        migrations.AlterField(
            model_name='animalgroup',
            name='strain',
            field=models.ForeignKey(to='assessment.Strain'),
        ),
        migrations.AlterField(
            model_name='dosegroup',
            name='dose_units',
            field=models.ForeignKey(to='assessment.DoseUnits'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
