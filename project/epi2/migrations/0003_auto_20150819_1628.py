# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0002_auto_20150819_1500'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ('name',), 'verbose_name_plural': 'Countries'},
        ),
        migrations.AlterModelOptions(
            name='criteria',
            options={'ordering': ('description',), 'verbose_name_plural': 'Criteria'},
        ),
        migrations.AlterModelOptions(
            name='ethnicity',
            options={'verbose_name_plural': 'Ethnicities'},
        ),
        migrations.RenameField(
            model_name='resultmeasurement',
            old_name='statistical_metric_description',
            new_name='metric_description'
        ),
    ]
