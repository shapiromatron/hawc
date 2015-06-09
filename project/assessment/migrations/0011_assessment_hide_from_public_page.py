# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0010_auto_20150507_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='hide_from_public_page',
            field=models.BooleanField(default=False, help_text=b'If public, anyone with a link can view, but do not show a link on the public-assessment page.'),
            preserve_default=True,
        ),
    ]
