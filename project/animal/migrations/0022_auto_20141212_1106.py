# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_generations(apps, schema_editor):
    AnimalGroup = apps.get_model("animal", "AnimalGroup")
    AnimalGroup.objects.filter(generation="F0").update(generation="P0")

def unupdate_generations(apps, schema_editor):
    AnimalGroup = apps.get_model("animal", "AnimalGroup")
    AnimalGroup.objects.filter(generation="P0").update(generation="F0")


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0021_auto_20141211_1525'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='species',
            options={'ordering': ('name',), 'verbose_name_plural': 'species'},
        ),
        migrations.AlterModelOptions(
            name='strain',
            options={'ordering': ('species', 'name')},
        ),
        migrations.AlterField(
            model_name='animalgroup',
            name='generation',
            field=models.CharField(default=b'', max_length=2, blank=True, choices=[(b'', b'N/A (not generational-study)'), (b'P0', b'Parent-generation (P0)'), (b'F1', b'First-generation (F1)'), (b'F2', b'Second-generation (F2)'), (b'F3', b'Third-generation (F3)'), (b'F4', b'Fourth-generation (F4)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='animalgroup',
            name='sex',
            field=models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'B', b'Both'), (b'R', b'Not reported')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='type',
            field=models.CharField(max_length=2, choices=[(b'Ac', b'Acute (<24 hr)'), (b'St', b'Short-term (1-30 days)'), (b'Sb', b'Subchronic (30-90 days)'), (b'Ch', b'Chronic (>90 days)'), (b'Ca', b'Cancer'), (b'Me', b'Mechanistic'), (b'Rp', b'Reproductive'), (b'Dv', b'Developmental'), (b'Ot', b'Other')]),
            preserve_default=True,
        ),
        migrations.RunPython(update_generations, reverse_code=unupdate_generations),
    ]
