# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0002_load_fixtures'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studypopulation',
            name='design',
            field=models.CharField(max_length=2, choices=[(b'CO', b'Cohort'), (b'CX', b'Cohort (Retrospective)'), (b'CY', b'Cohort (Prospective)'), (b'CC', b'Case-control'), (b'NC', b'Nested case-control'), (b'CR', b'Case report'), (b'SE', b'Case series'), (b'CT', b'Controlled trial'), (b'CS', b'Cross sectional')]),
        ),
    ]
