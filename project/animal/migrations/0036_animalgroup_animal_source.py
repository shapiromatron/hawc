# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def move_ani_source(apps, schema_editor):
    # from experiment to AnimalGroup
    AnimalGroup = apps.get_model("animal", "AnimalGroup")
    for ag in AnimalGroup.objects.all():
        ag.animal_source = ag.experiment.animal_source
        ag.save()

def unmove_ani_source(apps, schema_editor):
    # from first-animal group to Experiment
    Experiment = apps.get_model("animal", "Experiment")
    for exp in Experiment.objects.all():
        ag = exp.animal_groups.first()
        if ag:
            exp.animal_source = ag.animal_source
            exp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0035_auto_20150424_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalgroup',
            name='animal_source',
            field=models.CharField(help_text=b'Laboratory and/or breeding details where animals were acquired', max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(move_ani_source, reverse_code=unmove_ani_source),
        migrations.RemoveField(
            model_name='experiment',
            name='animal_source',
        ),
    ]
