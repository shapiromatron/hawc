# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0041_auto_20150519_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='dosingregime',
            name='duration_exposure_text',
            field=models.CharField(help_text=b'Text-description of the exposure duration (ex: 21 days, 104 wks, GD0 to PND9, GD0 to weaning)', max_length=128, verbose_name=b'Exposure duration (text)', blank=True),
            preserve_default=True,
        ),
    ]
