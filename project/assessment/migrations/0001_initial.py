# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name=b'Assessment Name')),
                ('cas', models.CharField(help_text=b'Add a CAS number if assessment is for one chemical, otherwise leave-blank.', max_length=40, verbose_name=b'Chemical identifier (CAS)', blank=True)),
                ('year', models.PositiveSmallIntegerField(verbose_name=b'Assessment Year')),
                ('version', models.CharField(max_length=80, verbose_name=b'Assessment Version')),
                ('editable', models.BooleanField(default=True, help_text=b'Team-members are allowed to edit assessment components.')),
                ('public', models.BooleanField(default=False, help_text=b'The assessment and all components are publicly assessable.')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-created',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BaseEndpoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name=b'Endpoint name')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('assessment', models.ForeignKey(to='assessment.Assessment')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EffectTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('slug', models.SlugField(help_text=b'The URL (web address) used to describe this object (no spaces or special-characters).', unique=True, max_length=128)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExternalImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_db', models.CharField(max_length=2, choices=[(b'DR', b'DRAGON')])),
                ('external_id', models.PositiveIntegerField()),
                ('external_table', models.CharField(max_length=40)),
                ('object_id', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('changed', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='baseendpoint',
            name='effects',
            field=models.ManyToManyField(to=b'assessment.EffectTag', null=True, verbose_name=b'Tags', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='project_manager',
            field=models.ManyToManyField(help_text=b'Have full assessment control, including the ability to add team members, make public, or delete an assessment.', related_name=b'pm+', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='reviewers',
            field=models.ManyToManyField(help_text=b'Can view assessment components in read-only mode; can also add comments.', related_name=b'r+', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='team_members',
            field=models.ManyToManyField(help_text=b'Can view and edit assessment components, when the project is editable.', related_name=b't+', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
