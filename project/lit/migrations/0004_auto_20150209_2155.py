# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lit', '0003_auto_20141010_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='description',
            field=models.TextField(help_text=b'A more detailed description of the literature search or import strategy.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='search',
            name='search_string',
            field=models.TextField(help_text=b'The search-text used to query an online database. Use colors to separate search-terms (optional).'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='search',
            name='source',
            field=models.PositiveSmallIntegerField(help_text=b'Database used to identify literature.', choices=[(0, b'Manually imported'), (1, b'PubMed'), (2, b'HERO')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='search',
            name='title',
            field=models.CharField(help_text=b'A brief-description to describe the identified literature.', max_length=128),
            preserve_default=True,
        ),
    ]
