# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0004_auto_20150205_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='study',
            name='ask_author',
            field=models.TextField(help_text=b'Details on correspondence between data-extractor and author, if needed.', verbose_name=b'Correspondence details', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='contact_author',
            field=models.BooleanField(default=False, help_text=b'Was the author contacted for clarification of methods or results?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='full_citation',
            field=models.TextField(help_text=b'Complete study citation, in desired format.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='published',
            field=models.BooleanField(default=False, help_text=b'If True, this study, risk-of-bias, and extraction details may be visible to reviewers and/or the general public (if assessment-permissions allow this level of visibility). Team-members and project-management can view both published and unpublished studies.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='short_citation',
            field=models.CharField(help_text=b'How the study should be identified (i.e. Smith et al. (2012), etc.)', max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='study_type',
            field=models.PositiveSmallIntegerField(help_text=b'Type of data captured in the selected study. This determines which fields are required for data-extraction.', choices=[(0, b'Animal Bioassay'), (1, b'Epidemiology'), (4, b'Epidemiology meta-analysis/pooled analysis'), (2, b'In vitro'), (3, b'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='study',
            name='summary',
            field=models.TextField(help_text=b'Study summary or details on data-extraction needs.', verbose_name=b'Summary and/or extraction requirements', blank=True),
            preserve_default=True,
        ),
    ]
