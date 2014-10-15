# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0002_change_related_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='enable_bmd',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='enable_comments',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='enable_data_extraction',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='enable_literature_review',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='enable_reference_values',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='enable_study_quality',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assessment',
            name='enable_summary_text',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
