# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0009_auto_20141031_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exposuregroup',
            name='fraction_male',
            field=models.FloatField(blank=True, help_text=b'Expects a value between 0 and 1, inclusive (leave blank if unknown)', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='exposuregroup',
            name='sex',
            field=models.CharField(max_length=1, choices=[(b'U', b'Not reported'), (b'M', b'Male'), (b'F', b'Female'), (b'B', b'Male and Female')]),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='fraction_male',
            field=models.FloatField(blank=True, help_text=b'Expects a value between 0 and 1, inclusive (leave blank if unknown)', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='sex',
            field=models.CharField(max_length=1, choices=[(b'U', b'Not reported'), (b'M', b'Male'), (b'F', b'Female'), (b'B', b'Male and Female')]),
        ),
    ]
