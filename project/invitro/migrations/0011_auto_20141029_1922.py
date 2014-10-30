# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0010_auto_20141029_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='ivendpoint',
            name='category',
            field=models.ForeignKey(related_name=b'endpoints', to='invitro.IVEndpointCategory', default=1),
            preserve_default=True,
        ),
    ]
