# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0011_statisticalmetric_islog'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assessedoutcomegroup',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='ethnicity',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='exposure',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='exposuregroup',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='factor',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='studycriteria',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='studypopulation',
            old_name='updated',
            new_name='last_updated',
        ),
    ]
