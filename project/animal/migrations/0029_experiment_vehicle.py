# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0028_auto_20150210_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='vehicle',
            field=models.CharField(help_text=b'If a vehicle was used, vehicle common-name', max_length=64, verbose_name=b'Chemical vehicle', blank=True),
            preserve_default=True,
        ),
    ]
