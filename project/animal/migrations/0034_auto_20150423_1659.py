# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations



def swap_sex(apps, schema_editor):
    AnimalGroup = apps.get_model("animal", "AnimalGroup")
    AnimalGroup.objects.filter(sex="B").update(sex="C")

def unswap_sex(apps, schema_editor):
    AnimalGroup = apps.get_model("animal", "AnimalGroup")
    AnimalGroup.objects.filter(sex="C").update(sex="B")


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0033_auto_20150407_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animalgroup',
            name='sex',
            field=models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'C', b'Combined'), (b'R', b'Not reported')]),
            preserve_default=True,
        ),
        migrations.RunPython(swap_sex, reverse_code=unswap_sex)
    ]

