# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0039_auto_20150427_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='diet',
            field=models.TextField(help_text=b'Description of animal-feed, if relevant', blank=True),
            preserve_default=True,
        ),
    ]
