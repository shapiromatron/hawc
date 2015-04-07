# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0032_auto_20150306_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dosingregime',
            name='negative_control',
            field=models.CharField(default=b'NR', help_text=b'Description of negative-controls used', max_length=2, choices=[(b'NR', b'Not-reported'), (b'UN', b'Untreated'), (b'VT', b'Vehicle-treated'), (b'B', b'Untreated + Vehicle-treated'), (b'Y', b'Yes (untreated and/or vehicle)'), (b'N', b'No')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dosingregime',
            name='route_of_exposure',
            field=models.CharField(help_text=b'Primary route of exposure. If multiple primary-exposures, describe in notes-field below', max_length=2, choices=[(b'OC', 'Oral capsule'), (b'OD', 'Oral diet'), (b'OG', 'Oral gavage'), (b'OW', 'Oral drinking water'), (b'I', 'Inhalation'), (b'D', 'Dermal'), (b'SI', 'Subcutaneous injection'), (b'IP', 'Intraperitoneal injection'), (b'IV', 'Intravenous injection'), (b'IO', 'in ovo'), (b'P', 'Parental'), (b'W', 'Whole body'), (b'M', 'Multiple'), (b'U', 'Unknown'), (b'O', 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='type',
            field=models.CharField(help_text=b'Type of study being performed; be as specific as-possible', max_length=2, choices=[(b'Ac', b'Acute (<24 hr)'), (b'St', b'Short-term (1-30 days)'), (b'Sb', b'Subchronic (30-90 days)'), (b'Ch', b'Chronic (>90 days)'), (b'Ca', b'Cancer'), (b'Me', b'Mechanistic'), (b'Rp', b'Reproductive'), (b'Dv', b'Developmental'), (b'Ot', b'Other'), (b'NR', b'Not-reported')]),
            preserve_default=True,
        ),
    ]
