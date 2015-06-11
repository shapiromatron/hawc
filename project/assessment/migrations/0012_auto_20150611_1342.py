# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0011_assessment_hide_from_public_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='assessment_objective',
            field=models.TextField(help_text=b'Describe the assessment objective(s), research questions, or clarification on the purpose of the assessment.', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='conflicts_of_interest',
            field=models.TextField(help_text=b'Describe any conflicts of interest by the assessment-team.', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='funding_source',
            field=models.TextField(help_text=b'Describe the funding-source(s) for this assessment.', blank=True),
            preserve_default=True,
        ),
    ]
