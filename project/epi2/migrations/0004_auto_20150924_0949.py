# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0003_auto_20150924_0933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='fraction_male',
        ),
        migrations.RemoveField(
            model_name='group',
            name='fraction_male_calculated',
        ),
        migrations.AddField(
            model_name='group',
            name='comments',
            field=models.TextField(help_text=b'Any other comments related to this group', blank=True),
        ),
        migrations.AlterField(
            model_name='groupresult',
            name='p_value',
            field=models.FloatField(blank=True, null=True, verbose_name=b'p-value', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AlterField(
            model_name='groupresult',
            name='p_value_qualifier',
            field=models.CharField(default=b'-', max_length=1, verbose_name=b'p-value qualifier', choices=[(b' ', b'-'), (b'-', b'n.s.'), (b'<', b'<'), (b'=', b'='), (b'>', b'>')]),
        ),
        migrations.AlterField(
            model_name='result',
            name='trend_test',
            field=models.CharField(help_text='Enter result, if available, ex: p\u22640.05', max_length=128, blank=True),
        ),
    ]
