# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0009_auto_20150209_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseendpoint',
            name='assessment',
            field=models.ForeignKey(to='assessment.Assessment', db_index=True),
            preserve_default=True,
        ),
    ]
