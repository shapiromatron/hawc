# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0006_ivendpoint'),
    ]

    operations = [
        migrations.CreateModel(
            name='IVEndpointGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dose', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('n', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('dose_group_id', models.PositiveSmallIntegerField()),
                ('difference_control', models.CharField(default=b'nc', max_length=2, choices=[(b'nc', b'no-change'), (b'-', b'decrease'), (b'+', b'increase'), (b'nt', b'not-tested')])),
                ('significant_control', models.CharField(default=b'nr', max_length=2, choices=[(b'nr', 'not reported'), (b'si', 'p \u2264 0.05'), (b'ns', 'not significant'), (b'na', 'not applicable')])),
                ('cytotoxicity_observed', models.CharField(default=b'nr', max_length=2, choices=[(b'nr', b'not reported'), (b'-', b'no'), (b'+', b'yes')])),
                ('response', models.FloatField(null=True, blank=True)),
                ('variance', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('endpoint', models.ForeignKey(related_name=b'groups', to='invitro.IVEndpoint')),
            ],
            options={
                'ordering': ('endpoint', 'dose_group_id'),
            },
            bases=(models.Model,),
        ),
    ]
