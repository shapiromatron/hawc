# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0013_auto_20150402_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ivchemical',
            name='precipitation',
        ),
        migrations.AlterField(
            model_name='ivendpoint',
            name='experiment',
            field=models.ForeignKey(related_name='endpoints', to='invitro.IVExperiment'),
            preserve_default=True,
        ),
    ]
