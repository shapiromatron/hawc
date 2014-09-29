# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0003_auto_20140922_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='enable_bmd',
            field=models.BooleanField(default=True, help_text=b"Conduct benchmark dose (BMD) modeling on animal bioassay data available in the HAWC database, using the US EPA's Benchmark Dose Modeling Software (BMDS).", verbose_name=b'Enable BMD modeling'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='enable_comments',
            field=models.BooleanField(default=True, help_text=b'Enable comments from reviewers or the general-public on datasets or findings; comment-functionality and visibility can be controlled in advanced-settings.'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='enable_data_extraction',
            field=models.BooleanField(default=True, help_text=b'Extract animal bioassay, epidemiological, or in-vitro data from key references and create customizable, dynamic visualizations or summary data and associated metadata for display.'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='enable_literature_review',
            field=models.BooleanField(default=True, help_text=b'Search or import references from PubMed and other literature databases, define inclusion, exclusion, or descriptive tags, and apply these tags to retrieved literature for your analysis.'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='enable_reference_values',
            field=models.BooleanField(default=True, help_text=b'Define a point-of-departure, apply uncertainty factors, and derive reference values by route of exposure.'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='enable_study_quality',
            field=models.BooleanField(default=True, help_text=b'Define criteria for a systematic review of literature, and apply these criteria to references in your literature-review. View details on findings and identify areas with a potential risk-of-bias.'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='enable_summary_text',
            field=models.BooleanField(default=True, help_text=b'Create custom-text to describe methodology and results of the assessment; insert tables, figures, and visualizations to using "smart-tags" which link to other data in HAWC.'),
        ),
    ]
