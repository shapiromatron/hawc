import json

from django.db import migrations


def forwards(apps, schema_editor):
    Visual = apps.get_model("summary", "visual")
    updates = []
    for visual in Visual.objects.filter(visual_type=5):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue
        settings["filters"] = []
        visual.settings = json.dumps(settings)
        updates.append(visual)
    if updates:
        Visual.objects.bulk_update(updates, ["settings"])


def backwards(apps, schema_editor):
    Visual = apps.get_model("summary", "visual")
    updates = []
    for visual in Visual.objects.filter(visual_type=5):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue
        settings.pop("filters")
        visual.settings = json.dumps(settings)
        updates.append(visual)
    if updates:
        Visual.objects.bulk_update(updates, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0039_update_rob_legend"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
