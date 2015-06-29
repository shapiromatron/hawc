# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessedoutcome',
            name='adjustment_factors',
            field=models.ManyToManyField(help_text=b'All factors which were included in final model', related_name='adjustments', to='epi.Factor', blank=True),
        ),
        migrations.AlterField(
            model_name='assessedoutcome',
            name='confounders_considered',
            field=models.ManyToManyField(help_text=b'All factors which were examined (including those which were included in final model)', related_name='confounders', verbose_name=b'Adjustment factors considered', to='epi.Factor', blank=True),
        ),
        migrations.AlterField(
            model_name='metaprotocol',
            name='exclusion_criteria',
            field=models.ManyToManyField(related_name='meta_exclusion_criteria', to='epi.StudyCriteria', blank=True),
        ),
        migrations.AlterField(
            model_name='metaprotocol',
            name='inclusion_criteria',
            field=models.ManyToManyField(related_name='meta_inclusion_criteria', to='epi.StudyCriteria', blank=True),
        ),
        migrations.AlterField(
            model_name='metaresult',
            name='adjustment_factors',
            field=models.ManyToManyField(help_text=b'All factors which were included in final model', related_name='meta_adjustments', to='epi.Factor', blank=True),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='confounding_criteria',
            field=models.ManyToManyField(related_name='confounding_criteria', to='epi.StudyCriteria', blank=True),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='exclusion_criteria',
            field=models.ManyToManyField(related_name='exclusion_criteria', to='epi.StudyCriteria', blank=True),
        ),
        migrations.AlterField(
            model_name='studypopulation',
            name='inclusion_criteria',
            field=models.ManyToManyField(related_name='inclusion_criteria', to='epi.StudyCriteria', blank=True),
        ),
    ]
