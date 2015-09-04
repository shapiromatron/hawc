# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0003_auto_20150903_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupresult',
            name='p_value_qualifier',
            field=models.CharField(default=b'-', max_length=1, verbose_name=b'p-value qualifier', choices=[(b' ', b' '), (b'-', b'n.s.'), (b'<', b'<'), (b'=', b'='), (b'>', b'>')]),
        ),
        migrations.AlterField(
            model_name='outcome',
            name='diagnostic',
            field=models.PositiveSmallIntegerField(choices=[(0, b'not reported'), (1, b'medical professional or test'), (2, b'medical records'), (3, b'self-reported'), (4, b'questionnaire'), (5, b'hospital admission'), (6, b'other')]),
        ),
    ]
