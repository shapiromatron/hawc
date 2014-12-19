# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0016_auto_20141210_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dosegroup',
            name='dose',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpointgroup',
            name='response',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpointgroup',
            name='variance',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individualanimal',
            name='response',
            field=models.FloatField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='referencevalue',
            name='aggregate_uf',
            field=models.FloatField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='referencevalue',
            name='point_of_departure',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='referencevalue',
            name='reference_value',
            field=models.FloatField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='uncertaintyfactorendpoint',
            name='value',
            field=models.FloatField(default=10.0, help_text=b'Note that 3*3=10 for all uncertainty value calculations; therefore specifying 3.33 is not required.', validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='uncertaintyfactorrefval',
            name='value',
            field=models.FloatField(default=10.0, help_text=b'Note that 3*3=10 for all uncertainty value calculations; therefore specifying 3.33 is not required.', validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=True,
        ),
    ]
