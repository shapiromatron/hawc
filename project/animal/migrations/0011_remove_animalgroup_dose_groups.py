# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0010_auto_20141103_1217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animalgroup',
            name='dose_groups',
        ),
    ]
