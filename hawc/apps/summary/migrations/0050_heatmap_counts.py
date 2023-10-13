# Generated by Django 4.2.6 on 2023-10-05 12:11

from django.db import migrations


def settings_json(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    changed = []
    for visual in Visual.objects.filter(visual_type=6):
        visual.settings["show_counts"] = 1
        changed.append(visual)
    if changed:
        Visual.objects.bulk_update(changed, ["settings"])


def reverse_settings_json(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    changed = []
    for visual in Visual.objects.filter(visual_type=6):
        visual.settings.pop("show_counts", None)
        changed.append(visual)
    if changed:
        Visual.objects.bulk_update(changed, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0049_alter_visual_settings"),
    ]

    operations = [
        migrations.RunPython(settings_json, reverse_code=reverse_settings_json),
    ]
