# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0007_ivendpointgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='IVBenchmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('benchmark', models.CharField(max_length=32)),
                ('value', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('endpoint', models.ForeignKey(related_name=b'benchmarks', to='invitro.IVEndpoint')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
