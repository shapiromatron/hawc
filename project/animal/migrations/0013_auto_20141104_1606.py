# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0012_auto_20141104_1530'),
    ]

    operations = [
        migrations.RenameField(
            model_name='animalgroup',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='dosegroup',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='doseunits',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='dosingregime',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='experiment',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='referencevalue',
            old_name='changed',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='strain',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='uncertaintyfactorendpoint',
            old_name='updated',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='uncertaintyfactorrefval',
            old_name='updated',
            new_name='last_updated',
        ),
    ]
