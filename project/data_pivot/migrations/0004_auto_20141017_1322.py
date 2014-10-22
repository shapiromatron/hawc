# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_pivot', '0003_auto_20141017_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datapivotquery',
            name='units',
            field=models.ForeignKey(blank=True, to='animal.DoseUnits', help_text=b'If kept-blank, dose-units will be random for each endpoint presented. This setting may used for comparing percent-response, where dose-units are not needed.', null=True),
        ),
    ]
