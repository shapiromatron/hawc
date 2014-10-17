# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_pivot', '0002_auto_20141017_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapivot',
            name='slug',
            field=models.SlugField(help_text=b'The URL (web address) used to describe this object (no spaces or special-characters).', verbose_name=b'URL Name'),
        ),
    ]
