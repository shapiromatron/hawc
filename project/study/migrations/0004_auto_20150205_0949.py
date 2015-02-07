# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0003_auto_20141104_1606'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studyqualitymetric',
            options={'ordering': ('domain', 'id')},
        ),
        migrations.AddField(
            model_name='studyqualitymetric',
            name='required_animal',
            field=models.BooleanField(default=True, help_text=b'Is this metric required for animal bioassay studies?', verbose_name=b'Required for bioassay?'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studyqualitymetric',
            name='required_epi',
            field=models.BooleanField(default=True, help_text=b'Is this metric required for human epidemiological studies?', verbose_name=b'Required for epidemiology?'),
            preserve_default=True,
        ),
    ]
