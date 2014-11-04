# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bmd', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bmd_session',
            options={'get_latest_by': 'last_updated'},
        ),
        migrations.RenameField(
            model_name='bmd_assessment_settings',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='bmd_session',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='logicfield',
            old_name='updated',
            new_name='last_updated',
        ),
    ]
