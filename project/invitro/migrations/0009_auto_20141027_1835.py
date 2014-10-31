# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0008_ivbenchmark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ivexperiment',
            name='dose_units',
            field=models.ForeignKey(related_name=b'ivexperiments', to='animal.DoseUnits'),
        ),
    ]
