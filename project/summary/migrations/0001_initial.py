# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SummaryText',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=255)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('title', models.CharField(max_length=128)),
                ('slug', models.SlugField(help_text=b'The URL (web address) used on the website to describe this object (no spaces or special-characters).', unique=True, verbose_name=b'URL Name')),
                ('text', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('assessment', models.ForeignKey(to='assessment.Assessment')),
            ],
            options={
                'verbose_name_plural': 'Summary Text Descriptions',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='summarytext',
            unique_together=set([('assessment', 'slug'), ('assessment', 'title')]),
        ),
    ]
