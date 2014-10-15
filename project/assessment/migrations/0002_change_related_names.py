# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='project_manager',
            field=models.ManyToManyField(help_text=b'Have full assessment control, including the ability to add team members, make public, or delete an assessment.', related_name=b'assessment_pms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='reviewers',
            field=models.ManyToManyField(help_text=b'Can view assessment components in read-only mode; can also add comments.', related_name=b'assessment_reviewers', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='team_members',
            field=models.ManyToManyField(help_text=b'Can view and edit assessment components, when the project is editable.', related_name=b'assessment_teams', null=True, to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
