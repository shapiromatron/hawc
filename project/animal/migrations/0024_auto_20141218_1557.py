# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0023_auto_20141212_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalgroup',
            name='lifestage_assessed',
            field=models.CharField(default='', help_text=b'Textual life-stage description when endpoints were measured (examples include: "parental, PND18, juvenile, adult, multiple")', max_length=32, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='animalgroup',
            name='lifestage_exposed',
            field=models.CharField(default='', help_text=b'Textual life-stage description when exposure occurred (examples include: "parental, PND18, juvenile, adult, continuous, multiple")', max_length=32, blank=True),
            preserve_default=False,
        ),
    ]
