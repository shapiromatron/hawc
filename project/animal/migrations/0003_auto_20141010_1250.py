# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0002_auto_20140918_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
