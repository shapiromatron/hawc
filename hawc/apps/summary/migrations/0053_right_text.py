from django.db import migrations


def set_right(apps, schema_editor):
    DataPivot = apps.get_model("summary", "DataPivot")
    updated_objs = []
    for obj in DataPivot.objects.all():
        for desc in obj.settings.get("description_settings", []):
            desc["to_right"] = False
        updated_objs.append(obj)
    DataPivot.objects.bulk_update(updated_objs, ["settings"])


def unset_right(apps, schema_editor):
    DataPivot = apps.get_model("summary", "DataPivot")
    updated_objs = []
    for obj in DataPivot.objects.all():
        for desc in obj.settings.get("description_settings", []):
            desc.pop("to_right")
        updated_objs.append(obj)
    DataPivot.objects.bulk_update(updated_objs, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0052_visual_image_alter_visual_visual_type"),
    ]

    operations = [
        migrations.RunPython(set_right, unset_right),
    ]
