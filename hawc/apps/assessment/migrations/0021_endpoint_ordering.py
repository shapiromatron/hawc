import json

from django.db import migrations


def check_sort(apps, schema_editor):
    """
    Previously, endpoints may be ordered arbitrarily, but now we're enforcing an order with querysets.
    Therefore, this migration loops through existing data pivots and alerts us of any which have
    no sorts applied, as this may indicate the order as presented may have changed.
    """
    for dp in apps.get_model("summary", "DataPivotQuery").objects.all():
        try:
            settings = json.loads(dp.settings)
        except json.JSONDecodeError:
            continue

        sort_fields = [f.get("field_name", None) for f in settings["sorts"]]
        sort_fields = [f for f in sort_fields if f and len(f) > 0]
        if len(sort_fields) == 0:
            print(
                f"Warning: Data pivot has no sort, output order may change: Assessment {dp.assessment_id} DP {dp.id}"
            )


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0020_job"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="baseendpoint",
            options={"ordering": ("id",)},
        ),
        migrations.RunPython(check_sort, reverse_code=migrations.RunPython.noop),
    ]
