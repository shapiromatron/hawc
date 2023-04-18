import json

from django.db import migrations


def add_filter(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updates = []
    failures = []

    for visual in Visual.objects.filter(visual_type=6):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            failures.append(visual.id)
            continue

        settings["filters"] = []
        settings["filtersLogic"] = "and"
        for column in settings["filter_widgets"]:
            column["header"] = ""
        for column in settings["table_fields"]:
            column["header"] = ""
        visual.settings = json.dumps(settings)
        updates.append(visual)

    Visual.objects.bulk_update(updates, ["settings"])
    print(f"{len(updates)} objects updated; {len(failures)} not updated: {failures}")


def remove_filter(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updates = []
    failures = []

    for visual in apps.get_model("summary", "Visual").objects.filter(visual_type=6):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            failures.append(visual.id)
            continue

        settings.pop("filters", None)
        settings.pop("filtersLogic", None)
        for column in settings["filter_widgets"]:
            column.pop("header", None)
        for column in settings["table_fields"]:
            column.pop("header", None)
        visual.settings = json.dumps(settings)
        updates.append(visual)

    Visual.objects.bulk_update(updates, ["settings"])
    print(f"{len(updates)} objects updated; {len(failures)} not updated: {failures}")


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0030_ept_migration"),
    ]

    operations = [
        migrations.RunPython(add_filter, reverse_code=remove_filter),
    ]
