# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0005_auto_20141015_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exposuregroup',
            name='exposure_n',
            field=models.PositiveSmallIntegerField(help_text=b'Final N used for exposure group', null=True, blank=True),
        ),
    ]
