# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lit', '0005_identifiers_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identifiers',
            name='database',
            field=models.IntegerField(choices=[(0, b'External link'), (1, b'PubMed'), (2, b'HERO')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='search',
            name='source',
            field=models.PositiveSmallIntegerField(help_text=b'Database used to identify literature.', choices=[(0, b'External link'), (1, b'PubMed'), (2, b'HERO')]),
            preserve_default=True,
        ),
    ]
