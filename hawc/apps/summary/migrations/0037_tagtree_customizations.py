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

        settings.update(
            show_legend=True,
            legend_position={"x": 25, "y": 25},
            show_counts=True,
            node_offsets={},
        )
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

        for setting in ["show_legend", "legend_position", "show_counts", "node_offsets"]:
            settings.pop(setting)

        visual.settings = json.dumps(settings)
        visual.save()


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0036_ept_summary_judgment_other"),
    ]

    operations = [
        migrations.RunPython(add_legend_settings, reverse_code=remove_legend_settings),
    ]
