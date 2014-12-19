# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0016_auto_20141125_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessedoutcome',
            name='dose_response',
            field=models.PositiveSmallIntegerField(default=0, help_text=b'Was a dose-response trend observed?', verbose_name=b'Dose Response Trend', choices=[(0, b'not-applicable'), (1, b'monotonic'), (2, b'non-monotonic'), (3, b'no trend'), (4, b'not reported')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='assessedoutcome',
            name='main_finding_support',
            field=models.PositiveSmallIntegerField(default=1, help_text=b'Are the results supportive of the main-finding?', choices=[(3, b'not-reported'), (2, b'supportive'), (1, b'inconclusive'), (0, b'not-supportive')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='exposuregroup',
            name='comparative_name',
            field=models.CharField(help_text=b'Should include effect-group and comparative group, for example "1.5-2.5(Q2) vs \xe2\x89\xa41.5(Q1)", or if only one group is available, "4.8\xc2\xb10.2 (mean\xc2\xb1SEM)"', max_length=64, verbose_name=b'Comparative Name', blank=True),
            preserve_default=True,
        ),
    ]
