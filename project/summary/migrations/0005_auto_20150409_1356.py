# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify
import json


def migrate_aggregations(apps, schema_editor):
    Aggregation = apps.get_model("animal", "Aggregation")
    Visual = apps.get_model("summary", "Visual")
    for agg in Aggregation.objects.all():
        kwargs = {
            "title": agg.name,
            "slug": slugify(agg.name),
            "assessment_id": agg.assessment_id,
            "visual_type": 0,
            "dose_units_id": agg.dose_units_id,
            "settings": json.dumps({"aggregation_type": agg.aggregation_type}),
            "caption": agg.summary_text,
            "created": agg.created,
            "last_updated": agg.last_updated,
        }
        eps = [e.baseendpoint_ptr_id for e in agg.endpoints.all()]

        v = Visual(**kwargs)
        v.save()
        v.endpoints.add(*eps)


def unmigrate_aggregations(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('summary', '0004_auto_20150409_1355'),
        ('animal', '0033_auto_20150407_1606'),
    ]

    operations = [
        migrations.RunPython(migrate_aggregations, reverse_code=unmigrate_aggregations),
    ]



