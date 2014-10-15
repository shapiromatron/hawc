# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),
        ('animal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataPivot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('slug', models.SlugField(help_text=b'The URL (web address) used to describe this object (no spaces or special-characters).', unique=True, verbose_name=b'URL Name')),
                ('settings', models.TextField(default=b'undefined', help_text=b'Paste content from a settings file from a different data-pivot, or keep set to "undefined" (this can be changed later).')),
                ('caption', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('title',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataPivotQuery',
            fields=[
                ('datapivot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data_pivot.DataPivot')),
                ('evidence_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'Animal Bioassay'), (1, b'Epidemiology'), (4, b'Epidemiology meta-analysis/pooled analysis'), (2, b'In vitro'), (3, b'Other')])),
                ('units', models.ForeignKey(to='animal.DoseUnits')),
            ],
            options={
            },
            bases=('data_pivot.datapivot',),
        ),
        migrations.CreateModel(
            name='DataPivotUpload',
            fields=[
                ('datapivot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='data_pivot.DataPivot')),
                ('file', models.FileField(help_text=b'The data should be in unicode-text format, tab delimited (this is a standard output type in Microsoft Excel).', upload_to=b'data_pivot')),
            ],
            options={
            },
            bases=('data_pivot.datapivot',),
        ),
        migrations.AddField(
            model_name='datapivot',
            name='assessment',
            field=models.ForeignKey(to='assessment.Assessment'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='datapivot',
            unique_together=set([('assessment', 'slug'), ('assessment', 'title')]),
        ),
    ]
