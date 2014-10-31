# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0007_auto_20141031_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='metaresult',
            name='data_location',
            field=models.CharField(default='', help_text=b'Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)', max_length=128, blank=True),
            preserve_default=False,
        ),
    ]
