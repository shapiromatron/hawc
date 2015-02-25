# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0009_auto_20150209_2121'),
        ('animal', '0031_auto_20150215_2049'),
        ('summary', '0002_auto_20141104_1606'),
        # ('data_pivot', '0006_auto_20150225_1409'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='DataPivot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('slug', models.SlugField(help_text=b'The URL (web address) used to describe this object (no spaces or special-characters).', verbose_name=b'URL Name')),
                ('settings', models.TextField(default=b'undefined', help_text=b'Paste content from a settings file from a different data-pivot, or keep set to "undefined".')),
                ('caption', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('title',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataPivotQuery',
            fields=[
                ('datapivot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='summary.DataPivot')),
                ('evidence_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'Animal Bioassay'), (1, b'Epidemiology'), (4, b'Epidemiology meta-analysis/pooled analysis'), (2, b'In vitro'), (3, b'Other')])),
                ('units', models.ForeignKey(blank=True, to='animal.DoseUnits', help_text=b'If kept-blank, dose-units will be random for each endpoint presented. This setting may used for comparing percent-response, where dose-units are not needed.', null=True)),
            ],
            options={
            },
            bases=('summary.datapivot',),
        ),
        migrations.CreateModel(
            name='DataPivotUpload',
            fields=[
                ('datapivot_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='summary.DataPivot')),
                ('file', models.FileField(help_text=b'The data should be in unicode-text format, tab delimited (this is a standard output type in Microsoft Excel).', upload_to=b'data_pivot')),
            ],
            options={
            },
            bases=('summary.datapivot',),
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

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
