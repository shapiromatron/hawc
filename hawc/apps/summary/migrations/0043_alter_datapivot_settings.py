import json

from django.db import migrations, models


def forwards(apps, schema_editor):
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        try:
            json.loads(dp.settings)
        except json.JSONDecodeError:
            dp.settings = "{}"
            updates.append(dp)
    if updates:
        DataPivot.objects.bulk_update(updates, ["settings"])


def backwards(apps, schema_editor):
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        settings = json.loads(dp.settings)
        if len(settings) == 0:
            dp.settings = "undefined"
            updates.append(dp)
    if updates:
        DataPivot.objects.bulk_update(updates, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0042_summarytable_interactive"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
        migrations.AlterField(
            model_name="datapivot",
            name="settings",
            field=models.JSONField(
                default=dict,
                blank=True,
                help_text="To clone settings from an existing data-pivot, copy them into this field, otherwise leave blank.",
            ),
        ),
    ]
