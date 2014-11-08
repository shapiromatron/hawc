# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0002_study_published'),
        ('invitro', '0002_auto_20141016_1541'),
    ]

    operations = [
        migrations.CreateModel(
            name='IVChemical',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('cas', models.CharField(max_length=40, verbose_name=b'Chemical identifier (CAS)', blank=True)),
                ('cas_inferred', models.BooleanField(default=False, help_text=b'Was the correct CAS inferred or incorrect in the original document?', verbose_name=b'CAS inferred?')),
                ('cas_notes', models.CharField(max_length=128, verbose_name=b'CAS determination notes')),
                ('source', models.CharField(max_length=128, verbose_name=b'Source of chemical')),
                ('purity', models.CharField(help_text=b'Example', max_length=32, verbose_name=b'Chemical purity')),
                ('purity_confirmed', models.BooleanField(default=False, verbose_name=b'Purity experimentally confirmed')),
                ('purity_confirmed_notes', models.TextField(blank=True)),
                ('dilution_storage_notes', models.TextField(help_text=b'Dilution, storage, and observations such as precipitation should be noted here.')),
                ('study', models.ForeignKey(related_name=b'ivchemicals', to='study.Study')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
