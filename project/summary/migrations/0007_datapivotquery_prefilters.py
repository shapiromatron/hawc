# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('summary', '0006_visual_prefilters'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapivotquery',
            name='prefilters',
            field=models.TextField(default=b'{}'),
            preserve_default=True,
        ),
    ]
