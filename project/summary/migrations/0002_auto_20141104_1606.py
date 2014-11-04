# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('summary', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='summarytext',
            old_name='updated',
            new_name='last_updated',
        ),
    ]
