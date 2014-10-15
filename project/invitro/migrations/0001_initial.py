# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0001_initial'),
        ('animal', '0001_initial'),
        ('assessment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CellType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EndpointGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('n', models.PositiveSmallIntegerField()),
                ('response', models.FloatField(null=True, blank=True)),
                ('stdev', models.FloatField(null=True, blank=True)),
                ('incidence', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sex', models.CharField(max_length=2, choices=[(b'm', b'Male'), (b'f', b'Female'), (b'b', b'Male and female'), (b'na', b'Not-applicable'), (b'nr', b'Not-reported')])),
                ('evidence_stream', models.CharField(max_length=1, choices=[(b'i', b'in vitro'), (b'e', b'ex vivo')])),
                ('generation', models.CharField(max_length=2, choices=[(b'f0', b'F0'), (b'f1', b'F1'), (b'f2', b'F2'), (b'na', b'Not-applicable')])),
                ('treatment_period', models.CharField(max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('cell_type', models.ForeignKey(to='invitro.CellType')),
                ('dose_units', models.ForeignKey(to='animal.DoseUnits')),
                ('species', models.ForeignKey(to='animal.Species')),
                ('strain', models.ForeignKey(blank=True, to='animal.Strain', null=True)),
                ('study', models.ForeignKey(related_name=b'ivexperiments', to='study.Study')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExposureGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.PositiveSmallIntegerField()),
                ('dose', models.FloatField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('experiment', models.ForeignKey(related_name=b'exposure_groups', to='invitro.Experiment')),
            ],
            options={
                'ordering': ('group_id',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IVEndpoint',
            fields=[
                ('baseendpoint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='assessment.BaseEndpoint')),
                ('diagnostic', models.CharField(max_length=256)),
                ('response_units', models.CharField(max_length=128)),
                ('data_type', models.CharField(max_length=2, choices=[(b'C', b'Continuous'), (b'D', b'Dichotomous')])),
                ('direction_of_effect', models.CharField(max_length=2, choices=[(b'u', b'Up'), (b'd', b'Down'), (b'i', b'Inconclusive'), (b'ui', b'Up/Inconclusive'), (b'di', b'Down/Inconclusive')])),
                ('loael', models.SmallIntegerField(default=-999)),
                ('noael', models.SmallIntegerField(default=-999)),
                ('target_process', models.CharField(max_length=256, verbose_name=b'Target Tissue/Physiological Process')),
                ('data_extracted', models.BooleanField(default=True, help_text=b'Dose-response data for endpoint are extracted in HAWC')),
                ('response_trend', models.CharField(max_length=2, choices=[(b'm', b'Monotonic'), (b'n', b'Non-monotonic'), (b'i', b'N/A')])),
                ('experiment', models.ForeignKey(related_name=b'endpoints', to='invitro.Experiment')),
            ],
            options={
            },
            bases=('assessment.baseendpoint',),
        ),
        migrations.AddField(
            model_name='endpointgroup',
            name='endpoint',
            field=models.ForeignKey(related_name=b'groups', to='invitro.IVEndpoint'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='endpointgroup',
            name='exposure_group',
            field=models.ForeignKey(to='invitro.ExposureGroup'),
            preserve_default=True,
        ),
    ]
