import json

from django.db import migrations


def add_patterns(apps, schema_editor):
    ids = []
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            continue

        for rect in settings["styles"]["rectangles"]:
            rect["pattern"] = "solid"
            dp.settings = json.dumps(settings)
            updates.append(dp)
            ids.append(dp.id)

    DataPivot.objects.bulk_update(updates, ["settings"])
    print(f"Updated the following data pivots: {ids}")


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0033_filter_query"),
    ]

    operations = [
        migrations.RunPython(add_patterns, reverse_code=migrations.RunPython.noop),
    ]
