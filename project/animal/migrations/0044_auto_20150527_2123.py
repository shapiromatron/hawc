# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def setNullResponses(apps, schema_editor):
    EndpointGroup = apps.get_model("animal", "EndpointGroup")
    count = EndpointGroup.objects\
                .filter(response=999, endpoint__data_type__in=["C", "P"])\
                .update(response=None)
    print "{} response updated".format(count)

def unsetNullResponses(apps, schema_editor):
    EndpointGroup = apps.get_model("animal", "EndpointGroup")
    count = EndpointGroup.objects\
                .filter(response__isnull=True, endpoint__data_type__in=["C", "P"])\
                .update(response=999)
    print "{} response updated".format(count)

def setNullNs(apps, schema_editor):
    EndpointGroup = apps.get_model("animal", "EndpointGroup")
    count = EndpointGroup.objects\
                .filter(n=999)\
                .update(n=None)
    print "{} N updated".format(count)

def unsetNullNs(apps, schema_editor):
    EndpointGroup = apps.get_model("animal", "EndpointGroup")
    count = EndpointGroup.objects\
                .filter(n__isnull=True)\
                .update(n=999)
    print "{} N updated".format(count)


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0043_auto_20150527_2051'),
    ]

    operations = [
        migrations.RunPython(setNullResponses, reverse_code=unsetNullResponses, atomic=False),
        migrations.RunPython(setNullNs, reverse_code=unsetNullNs, atomic=False),
    ]
