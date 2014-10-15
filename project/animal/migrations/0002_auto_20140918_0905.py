# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animalgroup',
            name='experiment',
            field=models.ForeignKey(related_name=b'animal_groups', to='animal.Experiment'),
        ),
    ]
