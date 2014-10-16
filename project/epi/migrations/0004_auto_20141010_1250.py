# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0003_auto_20140929_1053'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exposure',
            options={'ordering': ('exposure_form_definition',)},
        ),
        migrations.AlterModelOptions(
            name='studypopulation',
            options={'ordering': ('name',)},
        ),
    ]
