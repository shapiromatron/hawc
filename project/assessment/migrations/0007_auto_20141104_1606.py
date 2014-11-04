# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0006_auto_20141104_1504'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assessment',
            old_name='changed',
            new_name='last_updated',
        ),
        migrations.RenameField(
            model_name='baseendpoint',
            old_name='changed',
            new_name='last_updated',
        ),
    ]
