# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0031_auto_20150215_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpoint',
            name='response_units',
            field=models.CharField(help_text='Units the response was measured in (i.e., \u03bcg/dL, % control, etc.)', max_length=32, verbose_name=b'Response units'),
            preserve_default=True,
        ),
    ]
