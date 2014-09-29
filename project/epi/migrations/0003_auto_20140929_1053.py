# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0002_auto_20140919_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessedoutcome',
            name='main_finding',
            field=models.ForeignKey(blank=True,
                                    to='epi.ExposureGroup',
                                    help_text=b'When a study did not report a statistically significant association use the highest exposure group compared with the referent group (e.g., fourth quartile vs. first quartile). When a study reports a statistically significant association use the lowest exposure group with a statistically significant association (e.g., third quartile vs. first quartile). When associations were non-monotonic in nature, select main findings on a case-by-case basis.',
                                    null=True,
                                    verbose_name=b'Main finding'),
        ),
    ]
