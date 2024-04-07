from django.db import migrations

from hawc.apps.summary.constants import VisualType


def add_options(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updated_objs = []
    for obj in Visual.objects.filter(visual_type=VisualType.EXPLORE_HEATMAP):
        # totals
        totals = obj.settings.pop("show_totals", False)
        obj.settings["show_totals_x"] = totals
        obj.settings["show_totals_y"] = totals

        updated_objs.append(obj)

    Visual.objects.bulk_update(updated_objs, ["settings"])


def remove_options(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updated_objs = []
    for obj in Visual.objects.filter(visual_type=VisualType.EXPLORE_HEATMAP):
        # totals
        totals = bool(obj.settings.pop("show_totals_x") or obj.settings.pop("show_totals_y"))
        obj.settings["show_totals"] = totals

        updated_objs.append(obj)

    Visual.objects.bulk_update(updated_objs, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0054_dp_calculated_columns"),
    ]

    operations = [
        migrations.RunPython(add_options, remove_options),
    ]
