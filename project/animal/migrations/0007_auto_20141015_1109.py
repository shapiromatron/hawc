# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0006_auto_20141014_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endpoint',
            name='data_type',
            field=models.CharField(default=b'D', max_length=2, verbose_name=b'Dataset type', choices=[(b'C', b'Continuous'), (b'D', b'Dichotomous'), (b'DC', b'Dichotomous Cancer'), (b'NR', b'Not reported')]),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='monotonicity',
            field=models.PositiveSmallIntegerField(choices=[(0, b'N/A, single dose level study'), (1, b'N/A, no effects detected'), (2, b'yes, visual appearance of monotonicity but no trend'), (3, b'yes, monotonic and significant trend'), (4, b'yes, visual appearance of non-monotonic but no trend'), (5, b'yes, non-monotonic and significant trend'), (6, b'no pattern'), (7, b'unclear'), (8, b'not-reported')]),
        ),
    ]
