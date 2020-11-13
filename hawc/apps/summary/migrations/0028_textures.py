import json

from django.db import migrations


def add_patterns(apps, schema_editor):
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

    DataPivot.objects.bulk_update(updates, ["settings"])


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0027_tagtree_hide_empty_tag_nodes"),
    ]

    operations = [
        migrations.RunPython(add_patterns, reverse_code=migrations.RunPython.noop),
    ]
