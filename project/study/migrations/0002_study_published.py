# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='published',
            field=models.BooleanField(default=False, help_text=b'If True, reviewers and the public can see study (if assessment-permissions allow this level of visibility). Team-members can always see studies, even if they are not-yet published.'),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='study',
            options={'ordering': ('short_citation',), 'verbose_name_plural': 'Studies'},
        ),
    ]
