import json

from django.db import migrations

literature_tagtree = 4


def add_hide_empty_tag_nodes(apps, schema_editor):
    for visual in apps.get_model("summary", "Visual").objects.filter(
        visual_type=literature_tagtree
    ):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue

        settings["hide_empty_tag_nodes"] = False
        visual.settings = json.dumps(settings)
        visual.save()


def remove_hide_empty_tag_nodes(apps, schema_editor):
    for visual in apps.get_model("summary", "Visual").objects.filter(
        visual_type=literature_tagtree
    ):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue

        settings.pop("hide_empty_tag_nodes", None)
        visual.settings = json.dumps(settings)
        visual.save()


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0026_rob_heatmap_excludes"),
    ]

    operations = [
        migrations.RunPython(add_hide_empty_tag_nodes, reverse_code=remove_hide_empty_tag_nodes),
    ]
