import json

from django.db import migrations

literature_tagtree = 4


def add_legend_settings(apps, schema_editor):
    for visual in apps.get_model("summary", "Visual").objects.filter(
        visual_type=literature_tagtree
    ):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue

        settings["show_legend"] = True
        settings["show_counts"] = True
        visual.settings = json.dumps(settings)
        visual.save()


def remove_legend_settings(apps, schema_editor):
    for visual in apps.get_model("summary", "Visual").objects.filter(
        visual_type=literature_tagtree
    ):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue

        settings.pop("show_legend", None)
        settings.pop("show_counts", None)
        visual.settings = json.dumps(settings)
        visual.save()


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0036_ept_summary_judgment_other"),
    ]

    operations = [
        migrations.RunPython(add_legend_settings, reverse_code=remove_legend_settings),
    ]
