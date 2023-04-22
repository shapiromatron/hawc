import json

from django.db import migrations

sort_map = {True: "asc", False: "desc"}
unsort_map = {v: k for k, v in sort_map.items()}


def set_sorts(apps, schema_editor):
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            continue

        if len(settings["sorts"]) > 0:
            for row in settings["sorts"]:
                row["order"] = sort_map[row.pop("ascending")]
                row["custom"] = None
            dp.settings = json.dumps(settings)
            updates.append(dp)

    DataPivot.objects.bulk_update(updates, ["settings"])


def unset_sorts(apps, schema_editor):
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            continue

        if len(settings["sorts"]) > 0:
            for row in settings["sorts"]:
                row["ascending"] = unsort_map[row.pop("order")]
                row.pop("custom")
            dp.settings = json.dumps(settings)
            updates.append(dp)

    DataPivot.objects.bulk_update(updates, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0033_filter_query"),
    ]

    operations = [
        migrations.RunPython(set_sorts, reverse_code=unset_sorts),
    ]
