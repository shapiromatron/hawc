# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_pivot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapivot',
            name='settings',
            field=models.TextField(default=b'undefined', help_text=b'Paste content from a settings file from a different data-pivot, or keep set to "undefined".'),
        ),
    ]
