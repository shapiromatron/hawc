# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0019_auto_20141211_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generationalanimalgroup',
            name='animalgroup_ptr',
        ),
        migrations.RemoveField(
            model_name='generationalanimalgroup',
            name='parents',
        ),
        migrations.DeleteModel(
            name='GenerationalAnimalGroup',
        ),
        migrations.RenameField(
            model_name='animalgroup',
            old_name='generation_new',
            new_name='generation',
        ),
        migrations.RenameField(
            model_name='animalgroup',
            old_name='parents_new',
            new_name='parents',
        ),
    ]
