import json

from django.db import migrations

literature_tagtree = 4


def add_tagtree_size(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updates = []
    failures = []

    for visual in Visual.objects.filter(visual_type=literature_tagtree):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            failures.append(visual.id)
            continue

        settings.update(width=1280, height=800)
        visual.settings = json.dumps(settings)
        updates.append(visual)

    Visual.objects.bulk_update(updates, ["settings"])
    print(f"{len(updates)} objects updated; {len(failures)} not updated: {failures}")


def remove_tagtree_size(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updates = []
    failures = []

    for visual in Visual.objects.filter(visual_type=literature_tagtree):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            failures.append(visual.id)
            continue

        settings.pop("width")
        settings.pop("height")
        visual.settings = json.dumps(settings)
        updates.append(visual)

    Visual.objects.bulk_update(updates, ["settings"])
    print(f"{len(updates)} objects updated; {len(failures)} not updated: {failures}")


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0028_summarytable"),
    ]

    operations = [
        migrations.RunPython(add_tagtree_size, reverse_code=remove_tagtree_size),
    ]
