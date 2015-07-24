# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0002_auto_20150629_1327'),
        ('animal', '0010_auto_20150723_1536'),
    ]

    state_operations = [
        migrations.AlterField(
            model_name='exposure',
            name='metric_units',
            field=models.ForeignKey(to='assessment.DoseUnits'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
