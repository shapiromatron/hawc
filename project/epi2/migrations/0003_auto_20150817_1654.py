# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0002_auto_20150817_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(unique=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(unique=True, max_length=64),
        ),
    ]
