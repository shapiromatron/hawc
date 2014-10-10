# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lit', '0002_auto_20140929_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='search_string',
            field=models.TextField(help_text=b'The exact text used to search using an online database. Use colors to separate search-terms (optional).'),
        ),
    ]
