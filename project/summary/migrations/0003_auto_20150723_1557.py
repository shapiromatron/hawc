# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('summary', '0002_auto_20150629_1327'),
        ('animal', '0010_auto_20150723_1536'),
    ]

    state_operations = [
        migrations.AlterField(
            model_name='datapivotquery',
            name='units',
            field=models.ForeignKey(blank=True, to='assessment.DoseUnits', help_text=b'If kept-blank, dose-units will be random for each endpoint presented. This setting may used for comparing percent-response, where dose-units are not needed.', null=True),
        ),
        migrations.AlterField(
            model_name='visual',
            name='dose_units',
            field=models.ForeignKey(blank=True, to='assessment.DoseUnits', null=True),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
