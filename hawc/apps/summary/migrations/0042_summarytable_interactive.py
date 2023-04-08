from collections.abc import Callable

from django.db import migrations
from django.db.models import QuerySet

from hawc.apps.summary.constants import TableType


def update_settings(qs: QuerySet, field: str, updator: Callable):
    updates = []
    for item in qs:
        updator(getattr(item, field))
        updates.append(item)
    if updates:
        qs.model.objects.bulk_update(updates, [field])


def forwards(apps, schema_editor):
    qs = apps.get_model("summary", "summarytable").objects.filter(table_type=TableType.GENERIC)

    def update(content):
        content["interactive"] = False

    update_settings(qs, "content", update)


def backwards(apps, schema_editor):
    qs = apps.get_model("summary", "summarytable").objects.filter(table_type=TableType.GENERIC)

    def update(content):
        content.pop("interactive")

    update_settings(qs, "content", update)


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0041_summarytable_caption"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
