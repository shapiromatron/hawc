# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0008_auto_20141022_1652'),
        ('study', '0002_study_published'),
        ('invitro', '0004_ivcelltype'),
    ]

    operations = [
        migrations.CreateModel(
            name='IVExperiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transfection', models.CharField(help_text=b'Details on transfection methodology and details on genes or other genetic material introduced into assay, or "not-applicable"', max_length=256)),
                ('cell_line', models.CharField(help_text=b'Description of type of cell-line used (ex: primary cell-line, immortalized cell-line, stably transfected cell-line, transient transfected cell-line, etc.)', max_length=128)),
                ('dosing_notes', models.TextField(help_text=b'Notes describing dosing-protocol, including duration-details', blank=True)),
                ('metabolic_activation', models.CharField(default=b'nr', help_text=b'Was metabolic-activation used in system (ex: S9)?', max_length=2, choices=[(b'+', b'with metabolic activation'), (b'-', b'without metabolic activation'), (b'na', b'not applicable'), (b'nr', b'not reported')])),
                ('serum', models.CharField(max_length=128, verbose_name=b'Percent serum, serum-type, and/or description')),
                ('has_positive_control', models.BooleanField(default=False)),
                ('positive_control', models.CharField(help_text=b'Positive control chemical or other notes', max_length=128, blank=True)),
                ('has_negative_control', models.BooleanField(default=False)),
                ('negative_control', models.CharField(help_text=b'Negative control chemical or other notes', max_length=128, blank=True)),
                ('has_vehicle_control', models.BooleanField(default=False)),
                ('vehicle_control', models.CharField(help_text=b'Vehicle control chemical or other notes', max_length=128, blank=True)),
                ('control_notes', models.CharField(help_text=b'Additional details related to controls', max_length=128, blank=True)),
                ('cell_type', models.ForeignKey(related_name=b'ivexperiments', to='invitro.IVCellType')),
                ('dose_units', models.ForeignKey(related_name=b'+', to='animal.DoseUnits')),
                ('study', models.ForeignKey(related_name=b'ivexperiments', to='study.Study')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
