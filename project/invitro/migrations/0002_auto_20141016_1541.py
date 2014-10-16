# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='endpointgroup',
            name='endpoint',
        ),
        migrations.RemoveField(
            model_name='endpointgroup',
            name='exposure_group',
        ),
        migrations.DeleteModel(
            name='EndpointGroup',
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='cell_type',
        ),
        migrations.DeleteModel(
            name='CellType',
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='dose_units',
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='species',
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='strain',
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='study',
        ),
        migrations.RemoveField(
            model_name='exposuregroup',
            name='experiment',
        ),
        migrations.DeleteModel(
            name='ExposureGroup',
        ),
        migrations.RemoveField(
            model_name='ivendpoint',
            name='baseendpoint_ptr',
        ),
        migrations.RemoveField(
            model_name='ivendpoint',
            name='experiment',
        ),
        migrations.DeleteModel(
            name='Experiment',
        ),
        migrations.DeleteModel(
            name='IVEndpoint',
        ),
    ]
