# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0004_auto_20141010_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studypopulation',
            name='design',
            field=models.CharField(max_length=2, choices=[(b'CC', b'Case-control'), (b'CS', b'Cross-sectional'), (b'CP', b'Prospective'), (b'RT', b'Retrospective'), (b'CT', b'Controlled trial'), (b'SE', b'Case-series'), (b'CR', b'Case-report')]),
        ),
    ]
