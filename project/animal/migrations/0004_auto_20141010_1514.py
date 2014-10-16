# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0003_auto_20141010_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aggregation',
            name='summary_text',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='dosingregime',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='purity',
            field=models.FloatField(blank=True, help_text=b'Numeric-value only; assumed purity greater-than value specified (ex: >95.5%)', null=True, verbose_name=b'Chemical purity (%)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
