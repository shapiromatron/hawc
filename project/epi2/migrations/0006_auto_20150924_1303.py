# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0005_auto_20150924_1042'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exposure2',
            old_name='control_description',
            new_name='description',
        ),
    ]
