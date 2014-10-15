# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='metaresult',
            options={'ordering': ('label',)},
        ),
        migrations.AddField(
            model_name='metaresult',
            name='exposure_details',
            field=models.TextField(default='', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='metaresult',
            name='exposure_name',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='metaresult',
            name='label',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='metaprotocol',
            name='total_references',
            field=models.PositiveIntegerField(help_text=b'References identified through initial literature-search before application of inclusion/exclusion criteria', null=True, verbose_name=b'Total number of references found', blank=True),
        ),
    ]
