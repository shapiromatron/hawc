import json

from django.db import migrations

literature_tagtree = 4


def add_tagtree_size(apps, schema_editor):
    for visual in apps.get_model("summary", "Visual").objects.filter(
        visual_type=literature_tagtree
    ):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue

        settings.update(width=1280, height=800)
        visual.settings = json.dumps(settings)
        visual.save()


def remove_tagtree_size(apps, schema_editor):
    for visual in apps.get_model("summary", "Visual").objects.filter(
        visual_type=literature_tagtree
    ):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue

        settings.pop("width")
        settings.pop("height")
        visual.settings = json.dumps(settings)
        visual.save()


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0028_summarytable"),
    ]

    operations = [
        migrations.RunPython(add_tagtree_size, reverse_code=remove_tagtree_size),
    ]
