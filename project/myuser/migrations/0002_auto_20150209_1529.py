# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myuser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hawcuser',
            name='email',
            field=models.EmailField(unique=True, max_length=254, db_index=True),
            preserve_default=True,
        ),
    ]
