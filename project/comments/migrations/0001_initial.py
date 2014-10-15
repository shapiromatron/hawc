# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=256)),
                ('text', models.TextField()),
                ('slug', models.SlugField(help_text=b'The URL (web address) used to describe this object (no spaces or special-characters).', verbose_name=b'URL Name')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommentSettings',
            fields=[
                ('assessment', models.OneToOneField(related_name=b'comment_settings', primary_key=True, serialize=False, to='assessment.Assessment')),
                ('allow_comments', models.BooleanField(default=False, help_text=b'All logged-in users with access to the assessment will be able to provide comments on key assessment components,  including study-quality, endpoints, and summary-text.  Anonymous comments cannot be provided.')),
                ('public_comments', models.BooleanField(default=False, help_text=b'Any comments made will be viewable by anyone with access to the assessment. Associated responses to comments will also be presented. ')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comment',
            name='assessment',
            field=models.ForeignKey(to='assessment.Assessment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='commenter',
            field=models.ForeignKey(related_name=b'commenters', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
            preserve_default=True,
        ),
    ]
