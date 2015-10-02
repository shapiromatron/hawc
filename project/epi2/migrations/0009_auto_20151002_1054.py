# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi2', '0008_auto_20151001_1138'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('comparison_set', 'group_id')},
        ),
        migrations.AlterModelOptions(
            name='groupresult',
            options={'ordering': ('result', 'group__group_id')},
        ),
        migrations.RenameField(
            model_name='groupresult',
            old_name='measurement',
            new_name='result',
        ),
        migrations.RenameField(
            model_name='result',
            old_name='groups',
            new_name='comparison_set',
        ),
        migrations.RenameField(
            model_name='group',
            old_name='collection',
            new_name='comparison_set',
        ),
        migrations.AlterField(
            model_name='group',
            name='comparison_set',
            field=models.ForeignKey(related_name='comparison_set', to='epi2.ComparisonSet'),
        ),
        migrations.AlterField(
            model_name='comparisonset',
            name='exposure',
            field=models.ForeignKey(related_name='comparison_sets', blank=True, to='epi2.Exposure2', help_text=b'Exposure-group associated with this group', null=True),
        ),
        migrations.AlterField(
            model_name='comparisonset',
            name='outcome',
            field=models.ForeignKey(related_name='comparison_sets', to='epi2.Outcome', null=True),
        ),
        migrations.AlterField(
            model_name='comparisonset',
            name='study_population',
            field=models.ForeignKey(related_name='comparison_sets', to='epi2.StudyPopulation', null=True),
        ),
    ]
