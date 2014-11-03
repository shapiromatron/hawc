# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0008_auto_20141022_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='dosingregime',
            name='num_dose_groups',
            field=models.PositiveSmallIntegerField(default=4, verbose_name=b'Number of Dose Groups', validators=[django.core.validators.MinValueValidator(1)]),
            preserve_default=True,
        ),
    ]
