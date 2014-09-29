# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='search_string',
            field=models.TextField(help_text=b'The raw text of what was used to search using an online database. Use colors to separate search-terms (optional).'),
        ),
    ]
