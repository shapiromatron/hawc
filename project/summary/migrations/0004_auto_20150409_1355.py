# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0009_auto_20150209_2121'),
        ('animal', '0033_auto_20150407_1606'),
        ('summary', '0003_auto_20150225_1423'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visual',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('slug', models.SlugField(help_text=b'The URL (web address) used to describe this object (no spaces or special-characters).', verbose_name=b'URL Name')),
                ('visual_type', models.PositiveSmallIntegerField(choices=[(0, b'animal bioassay endpoint aggregation'), (1, b'animal bioassay endpoint crossview')])),
                ('settings', models.TextField(default=b'{}')),
                ('caption', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('assessment', models.ForeignKey(related_name='visuals', to='assessment.Assessment')),
                ('dose_units', models.ForeignKey(blank=True, to='animal.DoseUnits', null=True)),
                ('endpoints', models.ManyToManyField(help_text=b'Endpoints to be included in visualization', related_name='visuals', null=True, to='assessment.BaseEndpoint', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='visual',
            unique_together=set([('assessment', 'slug'), ('assessment', 'title')]),
        ),
    ]
