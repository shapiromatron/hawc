# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0020_auto_20141211_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpoint',
            name='animal_group',
            field=models.ForeignKey(related_name='endpoints', to='animal.AnimalGroup'),
            preserve_default=True,
        ),
    ]
