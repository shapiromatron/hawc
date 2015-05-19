# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0040_auto_20150511_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalgroup',
            name='comments',
            field=models.TextField(help_text=b'Any addition notes for this animal-group.', verbose_name=b'Description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='animalgroup',
            name='generation',
            field=models.CharField(default=b'', max_length=2, blank=True, choices=[(b'', b'N/A (not generational-study)'), (b'P0', b'Parent-generation (P0)'), (b'F1', b'First-generation (F1)'), (b'F2', b'Second-generation (F2)'), (b'F3', b'Third-generation (F3)'), (b'F4', b'Fourth-generation (F4)'), (b'Ot', b'Other')]),
            preserve_default=True,
        ),
    ]
