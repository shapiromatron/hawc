# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lit', '0005_auto_20151021_1624'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='identifiers',
            index_together=set([('database', 'unique_id')]),
        ),
    ]
