# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0008_auto_20150217_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='summary',
            field=models.TextField(help_text=b'Study summary or details on data-extraction needs.', verbose_name=b'Summary and/or extraction comments', blank=True),
            preserve_default=True,
        ),
    ]
