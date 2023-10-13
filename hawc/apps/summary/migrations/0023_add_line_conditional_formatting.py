import json

from django.db import migrations


def add_line_conditional_formatting(apps, schema_editor):
    for dp in apps.get_model("summary", "DataPivot").objects.all():
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            continue

        if "dataline_settings" in settings and len(settings["dataline_settings"]) > 0:
            settings["dataline_settings"][0]["conditional_formatting"] = []
            dp.settings = json.dumps(settings)
            dp.save()


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0022_add_new_visual"),
    ]

    operations = [
        migrations.RunPython(add_line_conditional_formatting),
    ]
