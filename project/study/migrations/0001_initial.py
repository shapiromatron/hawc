# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),
        ('lit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment', models.FileField(upload_to=b'study-attachment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('reference_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='lit.Reference')),
                ('study_type', models.PositiveSmallIntegerField(choices=[(0, b'Animal Bioassay'), (1, b'Epidemiology'), (4, b'Epidemiology meta-analysis/pooled analysis'), (2, b'In vitro'), (3, b'Other')])),
                ('short_citation', models.CharField(max_length=256)),
                ('full_citation', models.TextField()),
                ('coi_reported', models.PositiveSmallIntegerField(default=0, help_text=b'Was a conflict of interest reported by the study authors?', verbose_name=b'COI reported', choices=[(0, b'Authors report they have no COI'), (1, b'Authors disclosed COI'), (2, b'Unknown'), (3, b'Not reported')])),
                ('coi_details', models.TextField(help_text=b'Details related to potential or disclosed conflict(s) of interest', verbose_name=b'COI details', blank=True)),
                ('funding_source', models.TextField(blank=True)),
                ('study_identifier', models.CharField(help_text=b'Reference descriptor for assessment-tracking purposes (for example, "{Author, year, #EndnoteNumber}")', max_length=128, verbose_name=b'Internal study identifier', blank=True)),
                ('contact_author', models.BooleanField(default=False, help_text=b'Does author need to be contacted?')),
                ('ask_author', models.TextField(help_text=b'Details on author correspondence', blank=True)),
                ('summary', models.TextField(help_text=b'Study summary as written by team-members, or details on data-extraction requirements by project-management', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Studies',
            },
            bases=('lit.reference',),
        ),
        migrations.CreateModel(
            name='StudyQuality',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.PositiveSmallIntegerField(default=4, choices=[(1, b'Definitely high risk of bias'), (2, b'Probably high risk of bias'), (3, b'Probably low risk of bias'), (4, b'Definitely low risk of bias'), (0, b'Not applicable')])),
                ('notes', models.TextField(default=b'', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('study', 'metric'),
                'verbose_name_plural': 'Study Qualities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudyQualityDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('assessment', models.ForeignKey(related_name=b'sq_domains', to='assessment.Assessment')),
            ],
            options={
                'ordering': ('pk',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudyQualityMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('metric', models.CharField(max_length=256)),
                ('description', models.TextField(help_text=b'HTML text describing scoring of this field.', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('domain', models.ForeignKey(related_name=b'metrics', to='study.StudyQualityDomain')),
            ],
            options={
                'ordering': ('domain', 'metric'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='studyqualitydomain',
            unique_together=set([('assessment', 'name')]),
        ),
        migrations.AddField(
            model_name='studyquality',
            name='metric',
            field=models.ForeignKey(related_name=b'qualities', to='study.StudyQualityMetric'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studyquality',
            name='study',
            field=models.ForeignKey(related_name=b'qualities', to='study.Study'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='studyquality',
            unique_together=set([('study', 'metric')]),
        ),
        migrations.AddField(
            model_name='attachment',
            name='study',
            field=models.ForeignKey(related_name=b'attachments', to='study.Study'),
            preserve_default=True,
        ),
    ]
