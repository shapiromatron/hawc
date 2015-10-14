# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0002_load_fixtures'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupresult',
            options={'ordering': ('result', 'group__group_id')},
        ),
    ]
