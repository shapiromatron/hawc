# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0008_reporttemplate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='cas',
            field=models.CharField(help_text=b'Add a single CAS-number if one is available to describe the assessment, otherwise leave-blank.', max_length=40, verbose_name=b'Chemical identifier (CAS)', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='editable',
            field=models.BooleanField(default=True, help_text=b'Project-managers and team-members are allowed to edit assessment components.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='name',
            field=models.CharField(help_text=b'Describe the objective of the health-assessment.', max_length=80, verbose_name=b'Assessment Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='project_manager',
            field=models.ManyToManyField(help_text=b'Has complete assessment control, including the ability to add team members, make public, or delete an assessment. You can add multiple project-managers.', related_name='assessment_pms', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='public',
            field=models.BooleanField(default=False, help_text=b'The assessment can be viewed by the general public.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='reviewers',
            field=models.ManyToManyField(help_text=b'Can view the assessment even if the assessment is not public, but cannot add or change content. Reviewers may optionally add comments, if this feature is enabled. You can add multiple reviewers.', related_name='assessment_reviewers', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='team_members',
            field=models.ManyToManyField(help_text=b'Can view and edit assessment components, if project is editable. You can add multiple team-members', related_name='assessment_teams', null=True, to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='version',
            field=models.CharField(help_text=b'Version to describe the current assessment (i.e. draft, final, v1).', max_length=80, verbose_name=b'Assessment Version'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessment',
            name='year',
            field=models.PositiveSmallIntegerField(help_text=b'Year with which the assessment should be associated.', verbose_name=b'Assessment Year'),
            preserve_default=True,
        ),
    ]
