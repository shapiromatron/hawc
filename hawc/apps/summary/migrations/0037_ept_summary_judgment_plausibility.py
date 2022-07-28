from django.db import migrations


def change_ept_settings(apps, schema_editor):
    SummaryTable = apps.get_model("summary", "SummaryTable")
    updates = []

    for table in SummaryTable.objects.filter(table_type=1):
        # add plausibility, remove description
        table.content["summary_judgement"]["plausibility"] = "<p></p>"
        table.content["summary_judgement"].pop("description")
        updates.append(table)

    SummaryTable.objects.bulk_update(updates, ["content"])


def unchange_ept_settings(apps, schema_editor):
    SummaryTable = apps.get_model("summary", "SummaryTable")
    updates = []

    for table in SummaryTable.objects.filter(table_type=1):
        # add description, remove plausibility
        table.content["summary_judgement"]["description"] = "<p></p>"
        table.content["summary_judgement"].pop("plausibility")
        updates.append(table)

    SummaryTable.objects.bulk_update(updates, ["content"])


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0036_ept_summary_judgment_other"),
    ]

    operations = [
        migrations.RunPython(change_ept_settings, reverse_code=unchange_ept_settings),
    ]
