# -*- coding: utf-8 -*-


from django.db import migrations
from django.db.models import F, Func


def set_doi_lowercase(apps, schema_editor):
    Identifiers = apps.get_model("lit", "Identifiers")
    Identifiers.objects.filter(database=4).update(unique_id=Func(F("unique_id"), function="LOWER"))


class Migration(migrations.Migration):

    dependencies = [
        ("lit", "0015_unaccent"),
    ]

    operations = [
        migrations.RunPython(set_doi_lowercase, reverse_code=migrations.RunPython.noop),
    ]
