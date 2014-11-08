# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0005_changelog'),
        ('invitro', '0005_ivexperiment'),
    ]

    operations = [
        migrations.CreateModel(
            name='IVEndpoint',
            fields=[
                ('baseendpoint_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='assessment.BaseEndpoint')),
                ('assay_type', models.CharField(max_length=128)),
                ('short_description', models.CharField(help_text=b'Short (<64 character) description of effect & measurement', max_length=64)),
                ('data_location', models.CharField(help_text=b'Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)', max_length=128, blank=True)),
                ('data_type', models.CharField(default=b'C', max_length=2, verbose_name=b'Dataset type', choices=[(b'C', b'Continuous'), (b'D', b'Dichotomous'), (b'NR', b'Not reported')])),
                ('variance_type', models.PositiveSmallIntegerField(default=0, choices=[(0, b'NA'), (1, b'SD'), (2, b'SE')])),
                ('response_units', models.CharField(max_length=64, verbose_name=b'Response units')),
                ('observation_time', models.FloatField(default=-999)),
                ('observation_time_units', models.PositiveSmallIntegerField(default=0, choices=[(0, b'not-reported'), (1, b'seconds'), (2, b'minutes'), (3, b'hours'), (4, b'days'), (5, b'weeks'), (6, b'months')])),
                ('NOAEL', models.SmallIntegerField(default=-999, verbose_name=b'NOAEL')),
                ('LOAEL', models.SmallIntegerField(default=-999, verbose_name=b'NOAEL')),
                ('monotonicity', models.PositiveSmallIntegerField(default=8, choices=[(0, b'N/A, single dose level study'), (1, b'N/A, no effects detected'), (2, b'yes, visual appearance of monotonicity but no trend'), (3, b'yes, monotonic and significant trend'), (4, b'yes, visual appearance of non-monotonic but no trend'), (5, b'yes, non-monotonic and significant trend'), (6, b'no pattern'), (7, b'unclear'), (8, b'not-reported')])),
                ('overall_pattern', models.PositiveSmallIntegerField(default=0, choices=[(0, b'not-available'), (1, b'increase'), (2, b'increase, then decrease'), (3, b'decrease'), (4, b'decrease, then increase'), (5, b'no clear pattern')])),
                ('statistical_test_notes', models.CharField(help_text=b'Notes describing details on the statistical tests performed', max_length=256, blank=True)),
                ('trend_test', models.PositiveSmallIntegerField(default=0, choices=[(0, b'not-reported'), (1, b'not-analyzed'), (2, b'not-applicable'), (3, b'significant'), (4, b'not-significant')])),
                ('endpoint_notes', models.TextField(help_text=b'Any additional notes regarding the endpoint itself', blank=True)),
                ('result_notes', models.TextField(help_text=b'Qualitative description of the results', blank=True)),
                ('additional_fields', models.TextField(default=b'{}')),
                ('chemical', models.ForeignKey(related_name=b'endpoints', to='invitro.IVChemical')),
                ('experiment', models.ForeignKey(related_name=b'experiments', to='invitro.IVExperiment')),
            ],
            options={
            },
            bases=('assessment.baseendpoint',),
        ),
    ]
