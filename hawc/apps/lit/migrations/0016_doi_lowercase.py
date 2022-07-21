# -*- coding: utf-8 -*-


from django.db import migrations


def set_doi_lowercase(apps, schema_editor):
    Identifiers = apps.get_model("lit", "Identifiers")
    doi_ids = Identifiers.objects.filter(database=4)
    updates = []
    for ident in doi_ids:
        ident.unique_id = ident.unique_id.lower()
        updates.append(ident)

    Identifiers.objects.bulk_update(updates, ["unique_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("lit", "0015_unaccent"),
    ]

    operations = [
        migrations.RunPython(set_doi_lowercase, reverse_code=migrations.RunPython.noop),
    ]
