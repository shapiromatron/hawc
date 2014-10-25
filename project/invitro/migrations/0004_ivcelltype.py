# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0002_study_published'),
        ('invitro', '0003_ivchemical'),
    ]

    operations = [
        migrations.CreateModel(
            name='IVCellType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('species', models.CharField(max_length=64)),
                ('sex', models.CharField(max_length=2, choices=[(b'm', b'Male'), (b'f', b'Female'), (b'mf', b'Male and female'), (b'na', b'Not-applicable'), (b'nr', b'Not-reported')])),
                ('cell_type', models.CharField(max_length=64)),
                ('tissue', models.CharField(max_length=64)),
                ('source', models.CharField(max_length=128, verbose_name=b'Source of cell cultures')),
                ('study', models.ForeignKey(related_name=b'ivcelltypes', to='study.Study')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
