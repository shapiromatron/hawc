from django.db import migrations

NULL_VALUE = "---"


def settings_json(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    changed = []
    for visual in Visual.objects.filter(visual_type=6):
        visual.settings["count_column"] = NULL_VALUE
        changed.append(visual)
    if changed:
        Visual.objects.bulk_update(changed, ["settings"])


def reverse_settings_json(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    changed = []
    for visual in Visual.objects.filter(visual_type=6):
        visual.settings.pop("count_column", None)
        changed.append(visual)
    if changed:
        Visual.objects.bulk_update(changed, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0054_dp_calculated_columns"),
    ]

    operations = [
        migrations.RunPython(settings_json, reverse_code=reverse_settings_json),
    ]
