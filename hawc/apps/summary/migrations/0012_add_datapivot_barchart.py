# Generated by Django 1.10.5 on 2017-02-17 21:46


import json

from django.db import migrations


def add_barchart(apps, schema_editor):
    NULL_CASE = "---"
    DataPivot = apps.get_model("summary", "DataPivot")
    for obj in DataPivot.objects.all():
        try:
            settings = json.loads(obj.settings)
        except ValueError:
            settings = False

        if settings:
            # add barchart options
            settings["plot_settings"]["as_barchart"] = False
            settings["barchart"] = {
                "dpe": NULL_CASE,
                "field_name": NULL_CASE,
                "error_low_field_name": NULL_CASE,
                "error_high_field_name": NULL_CASE,
                "header_name": "",
                "error_header_name": "",
                "bar_style": "base",
                "error_marker_style": "base",
                "conditional_formatting": [],
                "error_show_tails": True,
            }

            # remove old row-overrides
            for row in settings["row_overrides"]:
                row.pop("offset", None)

            # add null rectangle style
            for item in settings["legend"]["fields"]:
                item["rect_style"] = NULL_CASE

            new_settings = json.dumps(settings)

            # don't change last_updated timestamp
            DataPivot.objects.filter(id=obj.id).update(settings=new_settings)


def remove_barchart(apps, schema_editor):
    DataPivot = apps.get_model("summary", "DataPivot")
    for obj in DataPivot.objects.all():
        try:
            settings = json.loads(obj.settings)
        except ValueError:
            settings = False

        if settings:
            settings["plot_settings"].pop("as_barchart")
            settings.pop("barchart")
            new_settings = json.dumps(settings)

            # don't change last_updated timestamp
            DataPivot.objects.filter(id=obj.id).update(settings=new_settings)


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0011_add_na_option"),
    ]

    operations = [
        migrations.RunPython(add_barchart, reverse_code=remove_barchart),
    ]
