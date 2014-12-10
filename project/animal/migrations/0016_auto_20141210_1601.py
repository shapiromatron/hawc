# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_null_significance(apps, schema_editor):
    EndpointGroup = apps.get_model("animal", "EndpointGroup")
    EndpointGroup.objects.filter(significance_level__lte=1E-5).update(significance_level=None)

def unset_null_significance(apps, schema_editor):
    EndpointGroup = apps.get_model("animal", "EndpointGroup")
    EndpointGroup.objects.filter(significance_level__isnull=True).update(significance_level=0.)


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0015_auto_20141210_1600'),
    ]

    operations = [
        migrations.RunPython(set_null_significance, reverse_code=unset_null_significance),
    ]
