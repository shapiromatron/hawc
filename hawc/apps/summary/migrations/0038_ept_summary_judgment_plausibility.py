from django.db import migrations


def change_ept_settings(apps, schema_editor):
    SummaryTable = apps.get_model("summary", "SummaryTable")
    updates = []

    for table in SummaryTable.objects.filter(table_type=1):
        table.content["summary_judgement"]["plausibility"] = "<p></p>"
        updates.append(table)

    SummaryTable.objects.bulk_update(updates, ["content"])


def unchange_ept_settings(apps, schema_editor):
    SummaryTable = apps.get_model("summary", "SummaryTable")
    updates = []

    for table in SummaryTable.objects.filter(table_type=1):
        table.content["summary_judgement"].pop("plausibility")
        updates.append(table)

    SummaryTable.objects.bulk_update(updates, ["content"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0037_tagtree_customizations"),
    ]

    operations = [
        migrations.RunPython(change_ept_settings, reverse_code=unchange_ept_settings),
    ]
