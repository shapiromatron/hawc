import json

from django.db import migrations

rob_types = [2, 3]


def add_exclude(apps, schema_editor):
    for visual in apps.get_model("summary", "Visual").objects.filter(visual_type__in=rob_types):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue

        settings["excluded_score_ids"] = []
        visual.settings = json.dumps(settings)
        visual.save()


def remove_exclude(apps, schema_editor):
    for visual in apps.get_model("summary", "Visual").objects.filter(visual_type__in=rob_types):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue

        settings.pop("excluded_score_ids", None)
        visual.settings = json.dumps(settings)
        visual.save()


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0025_auto_20200424_1304"),
    ]

    operations = [
        migrations.RunPython(add_exclude, reverse_code=remove_exclude),
    ]
