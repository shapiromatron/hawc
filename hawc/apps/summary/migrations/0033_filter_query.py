import json

from django.db import migrations

VISUAL_TYPES = [1, 6]  # crossview/heatmap


def add_query_string(apps, schema_editor):
    # add to visual
    Visual = apps.get_model("summary", "Visual")
    updates = []
    failures = []

    for visual in Visual.objects.filter(visual_type__in=VISUAL_TYPES):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            failures.append(visual.id)
            continue

        settings["filtersQuery"] = ""
        visual.settings = json.dumps(settings)
        updates.append(visual)

    Visual.objects.bulk_update(updates, ["settings"])
    print(f"{len(updates)} Visuals updated; {len(failures)} not updated: {failures}")

    # add to data pivot
    updates = []
    failures = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            failures.append(dp.id)
            continue

        if "plot_settings" in settings:
            if "filter_logic" not in settings["plot_settings"]:
                settings["plot_settings"]["filter_logic"] = "and"
            settings["plot_settings"]["filter_query"] = ""
            DataPivot.objects.filter(id=dp.id).update(settings=json.dumps(settings))
            updates.append(dp.id)
        else:
            failures.append(dp.id)
    print(f"{len(updates)} DataPivots updated; {len(failures)} not updated: {failures}")


def undo_query_string(apps, schema_editor):
    # add to visual
    Visual = apps.get_model("summary", "Visual")
    updates = []
    failures = []

    for visual in apps.get_model("summary", "Visual").objects.filter(visual_type__in=VISUAL_TYPES):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            failures.append(visual.id)
            continue

        settings.pop("filtersQuery")
        visual.settings = json.dumps(settings)
        updates.append(visual)

    Visual.objects.bulk_update(updates, ["settings"])
    print(f"{len(updates)} Visuals updated; {len(failures)} not updated: {failures}")

    # add to data pivot
    updates = []
    failures = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            failures.append(dp.id)
            continue

        if "plot_settings" in settings:
            settings["plot_settings"].pop("filter_query")
            DataPivot.objects.filter(id=dp.id).update(settings=json.dumps(settings))
            updates.append(dp.id)
        else:
            failures.append(dp.id)
    print(f"{len(updates)} DataPivot updated; {len(failures)} not updated: {failures}")


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0032_heatmap_axis_sorts"),
    ]

    operations = [
        migrations.RunPython(add_query_string, reverse_code=undo_query_string),
    ]
