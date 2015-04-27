# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0038_auto_20150424_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpoint',
            name='variance_type',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'NA'), (1, b'SD'), (2, b'SE'), (3, b'NR')]),
            preserve_default=True,
        ),
    ]
