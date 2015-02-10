# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0027_auto_20150210_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='dosingregime',
            name='negative_control',
            field=models.CharField(default=b'NR', help_text=b'Description of negative-controls used', max_length=2, choices=[(b'NR', b'Not-reported'), (b'UN', b'Untreated'), (b'VT', b'Vehicle-treated'), (b'B', b'Untreated + Vehicle-treated'), (b'N', b'None')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dosingregime',
            name='positive_control',
            field=models.NullBooleanField(default=None, help_text=b'Was a positive control used?', choices=[(True, b'Yes'), (False, b'No'), (None, b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='endpoint',
            name='diagnostic',
            field=models.TextField(help_text=b'Diagnostic or method used to measure endpoint (if relevant)', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='chemical',
            field=models.CharField(max_length=128, verbose_name=b'Chemical name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='chemical_source',
            field=models.CharField(max_length=128, verbose_name=b'Source of chemical', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='guideline_compliance',
            field=models.CharField(help_text=b'Description of any compliance methods used (i.e. use of EPA\n            OECD, NTP, or other guidelines; conducted under GLP guideline\n            conditions, non-GLP but consistent with guideline study, etc.)', max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dosingregime',
            name='route_of_exposure',
            field=models.CharField(max_length=2, choices=[(b'OC', 'Oral capsule'), (b'OD', 'Oral diet'), (b'OG', 'Oral gavage'), (b'OW', 'Oral drinking water'), (b'I', 'Inhalation'), (b'D', 'Dermal'), (b'SI', 'Subcutaneous injection'), (b'IP', 'Intraperitoneal injection'), (b'IO', 'in ovo'), (b'P', 'Parental'), (b'W', 'Whole body'), (b'U', 'Unknown'), (b'O', 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='purity_available',
            field=models.BooleanField(default=True, verbose_name=b'Chemical purity available?'),
            preserve_default=True,
        ),
    ]
