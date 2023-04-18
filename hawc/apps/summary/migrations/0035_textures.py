import json

from django.db import migrations


def add_patterns(apps, schema_editor):
    ids = []
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all().order_by("id"):
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            continue

        for rect in settings["styles"]["rectangles"]:
            rect["pattern"] = "solid"
            rect["pattern_fill"] = "#ffffff"

        dp.settings = json.dumps(settings)
        updates.append(dp)
        ids.append(dp.id)

    DataPivot.objects.bulk_update(updates, ["settings"])
    print(f"Updated the following {len(ids)} data pivots: {ids}")


def unadd_patterns(apps, schema_editor):
    ids = []
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all().order_by("id"):
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            continue

        for rect in settings["styles"]["rectangles"]:
            rect.pop("pattern")
            rect.pop("pattern_fill")

        dp.settings = json.dumps(settings)
        updates.append(dp)
        ids.append(dp.id)

    DataPivot.objects.bulk_update(updates, ["settings"])
    print(f"Updated the following {len(ids)} data pivots: {ids}")


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0034_sort_ordering"),
    ]

    operations = [
        migrations.RunPython(add_patterns, reverse_code=unadd_patterns),
    ]
