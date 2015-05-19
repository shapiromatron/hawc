# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('summary', '0007_datapivotquery_prefilters'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapivotquery',
            name='published_only',
            field=models.BooleanField(default=True, help_text=b'Only present data from studies which have been marked as "published" in HAWC.', verbose_name=b'Published studies only'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='datapivot',
            name='title',
            field=models.CharField(help_text=b'Enter the title of the visualization (spaces and special-characters allowed).', max_length=128),
            preserve_default=True,
        ),
    ]
