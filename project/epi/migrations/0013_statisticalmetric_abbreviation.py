# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0012_auto_20141104_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='statisticalmetric',
            name='abbreviation',
            field=models.CharField(default='add', max_length=32),
            preserve_default=False,
        ),
    ]
