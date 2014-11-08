# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def move_num_dgs(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    AnimalGroup = apps.get_model("animal", "AnimalGroup")
    for ag in AnimalGroup.objects.all():
        dr = ag.dosing_regime
        dr.num_dose_groups = ag.dose_groups
        dr.save()


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0009_dosingregime_num_dose_groups'),
    ]

    operations = [
        migrations.RunPython(move_num_dgs),
    ]
