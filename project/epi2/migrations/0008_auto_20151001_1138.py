# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0007_auto_20150924_1606'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ComparisonGroups',
            new_name='ComparisonSet',
        ),
    ]
