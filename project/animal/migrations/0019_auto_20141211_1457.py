# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def move_to_new_schema(apps, schema_editor):
    GenerationalAnimalGroup = apps.get_model("animal", "GenerationalAnimalGroup")
    for gag in GenerationalAnimalGroup.objects.all():
        gag.generation_new = gag.generation
        gag.save()

        ag_parents = []
        for parent in gag.parents.all():
            ag_parents.append(parent.animalgroup_ptr)

        if len(ag_parents)>0:
            gag.parents_new.add(*ag_parents)

class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0018_auto_20141211_1456'),
    ]

    operations = [
        migrations.RunPython(move_to_new_schema),
    ]
