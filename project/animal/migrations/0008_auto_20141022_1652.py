# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0007_auto_20141015_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dosingregime',
            name='route_of_exposure',
            field=models.CharField(max_length=2, choices=[(b'OD', 'Oral diet'), (b'OG', 'Oral gavage'), (b'OW', 'Oral drinking water'), (b'I', 'Inhalation'), (b'D', 'Dermal'), (b'SI', 'Subcutaneous injection'), (b'IP', 'Intraperitoneal injection'), (b'IO', 'in ovo'), (b'O', 'Other')]),
        ),
        migrations.AlterField(
            model_name='generationalanimalgroup',
            name='generation',
            field=models.CharField(max_length=2, choices=[(b'F0', b'Parent-generation (F0)'), (b'F1', b'First-generation (F1)'), (b'F2', b'Second-generation (F2)'), (b'F3', b'Third-generation (F3)'), (b'F4', b'Fourth-generation (F4)')]),
        ),
    ]
