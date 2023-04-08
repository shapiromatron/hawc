# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-08 16:09


import json

from django.db import migrations


def add_selected_metrics(apps, schema_editor):
    RiskOfBiasMetric = apps.get_model("riskofbias", "RiskOfBiasMetric")
    qs = apps.get_model("summary", "Visual").objects.filter(visual_type__in=[2, 3])

    for obj in qs:
        ids = RiskOfBiasMetric.objects.filter(domain__assessment_id=obj.assessment_id).values_list(
            "id", flat=True
        )

        settings = json.loads(obj.settings)
        settings["included_metrics"] = list(ids)
        obj.settings = json.dumps(settings)
        obj.save()


def remove_selected_metrics(apps, schema_editor):
    qs = apps.get_model("summary", "Visual").objects.filter(visual_type__in=[2, 3])
    for obj in qs:
        settings = json.loads(obj.settings)
        settings.pop("included_metrics")
        obj.settings = json.dumps(settings)
        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0007_auto_20160121_1507"),
    ]

    operations = [
        migrations.RunPython(add_selected_metrics, reverse_code=remove_selected_metrics),
    ]
