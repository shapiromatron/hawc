# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0026_auto_20150202_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animalgroup',
            name='duration_observation',
            field=models.FloatField(help_text=b'Numeric length of observation period, in days (fractions allowed)', null=True, verbose_name=b'Observation duration (days)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='animalgroup',
            name='name',
            field=models.CharField(help_text=b'Short description of the animals (i.e. Male Fischer F344 rats, Female C57BL/6 mice)', max_length=80),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dosingregime',
            name='description',
            field=models.TextField(help_text=b'Detailed description of dosing methodology (i.e. exposed via inhalation 5 days/week for 6 hours)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dosingregime',
            name='duration_exposure',
            field=models.FloatField(help_text=b'Numeric length of exposure period, in days (fractions allowed)', null=True, verbose_name=b'Exposure duration (days)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='FEL',
            field=models.SmallIntegerField(default=-999, help_text=b'Frank effect level', verbose_name=b'FEL'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='LOAEL',
            field=models.SmallIntegerField(default=-999, help_text=b'Lowest observed (adverse) effect level', verbose_name=b'LOAEL'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='NOAEL',
            field=models.SmallIntegerField(default=-999, help_text=b'No observed (adverse) effect level', verbose_name=b'NOAEL'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='effect',
            field=models.CharField(help_text=b'Effect, using common-vocabulary', max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='observation_time',
            field=models.FloatField(help_text=b'Numeric value of the time an observation was reported; optional, should be recorded if the same effect was measured multiple times.', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='organ',
            field=models.CharField(help_text=b'Relevant organ; also include tissue if relevant', max_length=128, verbose_name=b'Organ (and tissue)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='response_units',
            field=models.CharField(help_text='Units the response was measured in (i.e., \u03bcg/dL, % control, etc.)', max_length=15, verbose_name=b'Response units'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='system',
            field=models.CharField(help_text=b'Relevant biological system', max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='cas',
            field=models.CharField(help_text=b'CAS number for chemical-tested, if available.', max_length=40, verbose_name=b'Chemical identifier (CAS)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='description',
            field=models.TextField(help_text=b'Describe high-level experimental protocol used. Other fields are available in subsequent forms to enter the species, strain, and dosing-protocol. However, this may be a useful field to describe the overall purpose and experimental design.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='name',
            field=models.CharField(help_text=b'Short-text used to describe the experiment (i.e. 2-year cancer bioassay, 28-day inhalation, etc.).', max_length=80),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='purity_available',
            field=models.BooleanField(default=True, help_text=b'Was the purity of the chemical described in the study?', verbose_name=b'Chemical purity available?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='type',
            field=models.CharField(help_text=b'Type of study being performed; be as specific as-possible', max_length=2, choices=[(b'Ac', b'Acute (<24 hr)'), (b'St', b'Short-term (1-30 days)'), (b'Sb', b'Subchronic (30-90 days)'), (b'Ch', b'Chronic (>90 days)'), (b'Ca', b'Cancer'), (b'Me', b'Mechanistic'), (b'Rp', b'Reproductive'), (b'Dv', b'Developmental'), (b'Ot', b'Other')]),
            preserve_default=True,
        ),
    ]
