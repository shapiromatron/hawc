# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_pivot', '0004_auto_20141017_1322'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datapivot',
            old_name='updated',
            new_name='last_updated',
        ),
    ]
