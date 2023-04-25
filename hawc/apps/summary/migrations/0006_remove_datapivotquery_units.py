

from django.db import migrations


def units_to_list(apps, schema_editor):
    for dp in apps.get_model("summary", "DataPivotQuery").objects.all():
        if dp.units_id:
            dp.preferred_units = [dp.units_id]
            dp.save()


def units_from_list(apps, schema_editor):
    for dp in apps.get_model("summary", "DataPivotQuery").objects.all():
        if len(dp.preferred_units) > 0:
            dp.units_id = dp.preferred_units[0]
            dp.save()


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0005_datapivotquery_preferred_units"),
    ]

    operations = [
        migrations.RunPython(units_to_list, reverse_code=units_from_list),
    ]
