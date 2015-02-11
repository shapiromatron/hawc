# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0029_experiment_vehicle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dosingregime',
            name='duration_exposure',
            field=models.FloatField(help_text=b'Length of exposure period (fractions allowed), used for sorting in visualizations', null=True, verbose_name=b'Exposure duration (days)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dosingregime',
            name='num_dose_groups',
            field=models.PositiveSmallIntegerField(default=4, help_text=b'Number of dose groups, plus control', verbose_name=b'Number of Dose Groups', validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dosingregime',
            name='route_of_exposure',
            field=models.CharField(help_text=b'Primary route of exposure. If multiple primary-exposures, describe in notes-field below', max_length=2, choices=[(b'OC', 'Oral capsule'), (b'OD', 'Oral diet'), (b'OG', 'Oral gavage'), (b'OW', 'Oral drinking water'), (b'I', 'Inhalation'), (b'D', 'Dermal'), (b'SI', 'Subcutaneous injection'), (b'IP', 'Intraperitoneal injection'), (b'IO', 'in ovo'), (b'P', 'Parental'), (b'W', 'Whole body'), (b'M', 'Multiple'), (b'U', 'Unknown'), (b'O', 'Other')]),
            preserve_default=True,
        ),
    ]
