# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0034_auto_20150423_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='description',
            field=models.TextField(help_text=b'Text-description of the experimental protocol used. May also include information such as animal husbandry. Note that dosing-regime information and animal details are captured in other fields.', verbose_name=b'Description and animal husbandry', blank=True),
            preserve_default=True,
        ),
    ]
