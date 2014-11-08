# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0011_auto_20141029_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ivendpoint',
            name='category',
            field=models.ForeignKey(related_name=b'endpoints', to='invitro.IVEndpointCategory'),
        ),
    ]
