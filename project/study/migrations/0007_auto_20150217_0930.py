# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0006_auto_20150217_0814'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='studyquality',
            unique_together=set([]),
        ),
    ]
