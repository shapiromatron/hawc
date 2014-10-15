# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import lit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Identifiers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('unique_id', models.IntegerField()),
                ('database', models.IntegerField(choices=[(0, b'Manually imported'), (1, b'PubMed'), (2, b'HERO')])),
                ('content', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PubMedQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('results', models.TextField(blank=True)),
                ('query_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-query_date'],
                'get_latest_by': 'query_date',
                'verbose_name_plural': 'PubMed Queries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(blank=True)),
                ('authors', models.TextField(blank=True)),
                ('year', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('journal', models.TextField(blank=True)),
                ('abstract', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('block_id', models.DateTimeField(help_text=b'Used internally for determining when reference was originally added', null=True, blank=True)),
                ('assessment', models.ForeignKey(related_name=b'references', to='assessment.Assessment')),
                ('identifiers', models.ManyToManyField(related_name=b'references', to='lit.Identifiers', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferenceFilterTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(max_length=100, verbose_name='Slug')),
                ('path', models.CharField(unique=True, max_length=255)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferenceTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_object', models.ForeignKey(to='lit.Reference')),
                ('tag', models.ForeignKey(related_name=b'lit_referencetags_items', to='lit.ReferenceFilterTag')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('search_type', models.CharField(max_length=1, choices=[(b's', b'Search'), (b'i', b'Import')])),
                ('source', models.PositiveSmallIntegerField(choices=[(0, b'Manually imported'), (1, b'PubMed'), (2, b'HERO')])),
                ('title', models.CharField(max_length=128)),
                ('slug', models.SlugField(help_text=b'The URL (web address) used to describe this object (no spaces or special-characters).', verbose_name=b'URL Name')),
                ('description', models.TextField()),
                ('search_string', models.TextField(help_text=b'The raw text of what was used to search using an online database')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('assessment', models.ForeignKey(related_name=b'literature_searches', to='assessment.Assessment')),
            ],
            options={
                'ordering': ['-last_updated'],
                'get_latest_by': ('last_updated',),
                'verbose_name_plural': 'searches',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='search',
            unique_together=set([('assessment', 'slug'), ('assessment', 'title')]),
        ),
        migrations.AddField(
            model_name='reference',
            name='searches',
            field=models.ManyToManyField(related_name=b'references', to='lit.Search'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reference',
            name='tags',
            field=lit.managers.ReferenceFilterTagManager(to='lit.ReferenceFilterTag', through='lit.ReferenceTags', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pubmedquery',
            name='search',
            field=models.ForeignKey(to='lit.Search'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='identifiers',
            unique_together=set([('database', 'unique_id')]),
        ),
    ]
