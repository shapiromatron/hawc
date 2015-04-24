# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0037_auto_20150424_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpoint',
            name='endpoint_notes',
            field=models.TextField(help_text=b'Any additional notes related to this endpoint/methodology, not including results', verbose_name=b'General notes/methodology', blank=True),
            preserve_default=True,
        ),
    ]
