import json

from django.db import migrations

rob_visual_types = (2, 3)


def change_legend_settings(apps, schema_editor):
    for visual in apps.get_model("summary", "visual").objects.filter(
        visual_type__in=rob_visual_types
    ):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue
        legend_x = settings.get("legend_x", None)
        legend_y = settings.get("legend_y", None)
        if legend_x == -1 and legend_y == 9999:
            settings["legend_x"] = 9999
            settings["legend_y"] = 9999
            settings["padding_right"] = 330
        visual.settings = json.dumps(settings)
        visual.save()


def unchange_legend_settings(apps, schema_editor):
    for visual in apps.get_model("summary", "visual").objects.filter(
        visual_type__in=rob_visual_types
    ):
        try:
            settings = json.loads(visual.settings)
        except json.JSONDecodeError:
            continue
        legend_x = settings.get("legend_x", None)
        legend_y = settings.get("legend_y", None)
        if legend_x == 9999 and legend_y == 9999:
            settings["legend_x"] = -1
            settings["legend_y"] = 9999
            settings["padding_right"] = 25
        visual.settings = json.dumps(settings)
        visual.save()


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0038_ept_summary_judgment_plausibility"),
    ]

    operations = [
        migrations.RunPython(change_legend_settings, reverse_code=unchange_legend_settings),
    ]
