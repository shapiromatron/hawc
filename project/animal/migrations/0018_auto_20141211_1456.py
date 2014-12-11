# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0017_auto_20141211_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalgroup',
            name='generation_new',
            field=models.CharField(default=b'', max_length=2, blank=True, choices=[(b'', b'N/A (not generational-study)'), (b'F0', b'Parent-generation (F0)'), (b'F1', b'First-generation (F1)'), (b'F2', b'Second-generation (F2)'), (b'F3', b'Third-generation (F3)'), (b'F4', b'Fourth-generation (F4)')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='animalgroup',
            name='parents_new',
            field=models.ManyToManyField(related_name='children', null=True, to='animal.AnimalGroup', blank=True),
            preserve_default=True,
        ),
    ]
