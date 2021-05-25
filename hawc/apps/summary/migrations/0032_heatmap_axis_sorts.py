from itertools import chain
import json

from django.db import migrations

literature_tagtree = 6


def add_heatmap_axis(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updates = []
    failures = []

    for visual in Visual.objects.filter(visual_type=6):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            failures.append(visual.id)
            continue

        for field in chain(settings["x_fields"], settings["y_fields"]):
            field["items"] = None
        visual.settings = json.dumps(settings)
        updates.append(visual)

    Visual.objects.bulk_update(updates, ["settings"])
    print(f"{len(updates)} objects updated; {len(failures)} not updated: {failures}")


def undo_heatmap_axis(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updates = []
    failures = []

    for visual in apps.get_model("summary", "Visual").objects.filter(visual_type=6):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            failures.append(visual.id)
            continue

        for field in chain(settings["x_fields"], settings["y_fields"]):
            field.pop("items")
        visual.settings = json.dumps(settings)
        updates.append(visual)

    Visual.objects.bulk_update(updates, ["settings"])
    print(f"{len(updates)} objects updated; {len(failures)} not updated: {failures}")


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0031_heatmap_filters"),
    ]

    operations = [
        migrations.RunPython(add_heatmap_axis, reverse_code=undo_heatmap_axis),
    ]
