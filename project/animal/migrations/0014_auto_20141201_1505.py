# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0013_auto_20141104_1606'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dosegroup',
            options={'ordering': ('dose_units', 'dose_group_id')},
        ),
    ]
