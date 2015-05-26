# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('summary', '0009_auto_20150520_0959'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='datapivot',
            unique_together=set([('assessment', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='visual',
            unique_together=set([('assessment', 'slug')]),
        ),
    ]
