# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0002_study_published'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studyquality',
            old_name='changed',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='studyqualitydomain',
            old_name='changed',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='studyqualitymetric',
            old_name='changed',
            new_name='last_updated',
        ),
    ]
