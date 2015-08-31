# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0002_auto_20150828_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultmetric',
            name='showForestPlot',
            field=models.BooleanField(default=True, help_text=b'Does forest-plot representation of result make sense?', verbose_name=b'Show on forest plot'),
        ),
        migrations.AlterField(
            model_name='groupresult',
            name='p_value_qualifier',
            field=models.CharField(default=b'-', max_length=1, verbose_name=b'p-value qualifier', choices=[(b'-', b'n.s.'), (b'<', b'<'), (b'=', b'=')]),
        ),
    ]
