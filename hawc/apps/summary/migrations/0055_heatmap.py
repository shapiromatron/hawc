from itertools import chain

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
        # color legend
        obj.settings["color_legend"] = "none"
        # unique on
        obj.settings["unique_on"] = "index"
        # extra columns + subtotal
        for item in chain(obj.settings.get("x_fields", []), obj.settings.get("y_fields", [])):
            item["extra_columns"] = ""
            item["subtotal"] = False
        # filter widget height
        for item in obj.settings.get("filter_widgets", []):
            item["height"] = 8

        updated_objs.append(obj)

    Visual.objects.bulk_update(updated_objs, ["settings"])


def remove_options(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    updated_objs = []
    for obj in Visual.objects.filter(visual_type=VisualType.EXPLORE_HEATMAP):
        # totals
        totals = bool(obj.settings.pop("show_totals_x") or obj.settings.pop("show_totals_y"))
        obj.settings["show_totals"] = totals
        # color legend
        obj.settings.pop("color_legend")
        # unique on
        obj.settings.pop("unique_on")
        # extra columns + subtotal
        for item in chain(obj.settings.get("x_fields", []), obj.settings.get("y_fields", [])):
            item.pop("extra_columns")
            item.pop("subtotal")
        # filter widget height
        for item in obj.settings.get("filter_widgets", []):
            item.pop("height")

        updated_objs.append(obj)

    Visual.objects.bulk_update(updated_objs, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0054_dp_calculated_columns"),
    ]

    operations = [
        migrations.RunPython(add_options, remove_options),
    ]
