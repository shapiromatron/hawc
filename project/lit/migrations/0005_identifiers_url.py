# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lit', '0004_auto_20150209_2155'),
    ]

    operations = [
        migrations.AddField(
            model_name='identifiers',
            name='url',
            field=models.URLField(blank=True),
            preserve_default=True,
        ),
    ]
