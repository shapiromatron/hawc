# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0005_changelog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='externalimport',
            name='content_type',
        ),
        migrations.DeleteModel(
            name='ExternalImport',
        ),
    ]
