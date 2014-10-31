# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0010_auto_20141031_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='statisticalmetric',
            name='isLog',
            field=models.BooleanField(default=True, help_text=b'When  plotting, use a log base 10 scale', verbose_name=b'Log-results'),
            preserve_default=True,
        ),
    ]
