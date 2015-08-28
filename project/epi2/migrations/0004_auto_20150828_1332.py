# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0003_auto_20150828_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupcollection',
            name='outcome',
            field=models.ForeignKey(related_name='group_collections', to='epi2.Outcome', null=True),
        ),
        migrations.AlterField(
            model_name='groupcollection',
            name='study_population',
            field=models.ForeignKey(related_name='group_collections', to='epi2.StudyPopulation', null=True),
        ),
    ]
