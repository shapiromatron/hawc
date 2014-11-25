# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0015_auto_20141119_1428'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='singleresult',
            options={},
        ),
        migrations.RenameField(
            model_name='metaresult',
            old_name='risk_estimate',
            new_name='estimate',
        ),
        migrations.RenameField(
            model_name='singleresult',
            old_name='risk_estimate',
            new_name='estimate',
        ),
    ]
