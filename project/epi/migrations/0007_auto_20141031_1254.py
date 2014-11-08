# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0006_auto_20141023_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='factor',
            name='description',
            field=models.TextField(),
        ),
    ]
