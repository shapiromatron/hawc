# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('summary', '0005_auto_20150409_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='visual',
            name='prefilters',
            field=models.TextField(default=b'{}'),
            preserve_default=True,
        ),
    ]
