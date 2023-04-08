import json

from django.db import migrations, models


def typeConvertPubmedResults(apps, schema_editor, type_):
    PubMedQuery = apps.get_model("lit", "PubMedQuery")
    for qry in PubMedQuery.objects.all():
        results = json.loads(qry.results)
        if results["removed"] is None:
            results["removed"] = []
        qry.results = json.dumps(
            {
                "ids": [type_(id_) for id_ in results["ids"]],
                "added": [type_(id_) for id_ in results["added"]],
                "removed": [type_(id_) for id_ in results["removed"]],
            }
        )
        qry.save()


def typeConvertPubmedResultsToStr(apps, schema_editor):
    typeConvertPubmedResults(apps, schema_editor, str)


def typeConvertPubmedResultsToInt(apps, schema_editor):
    typeConvertPubmedResults(apps, schema_editor, int)


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0006_auto_20151021_1626"),
    ]

    operations = [
        migrations.AlterField(
            model_name="identifiers",
            name="database",
            field=models.IntegerField(
                choices=[
                    (0, b"External link"),
                    (1, b"PubMed"),
                    (2, b"HERO"),
                    (3, b"RIS (Endnote/Refman)"),
                    (4, b"DOI"),
                    (5, b"Web of Science"),
                    (6, b"Scopus"),
                    (7, b"Embase"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="identifiers",
            name="unique_id",
            field=models.CharField(max_length=256, db_index=True),
        ),
        migrations.AlterField(
            model_name="search",
            name="source",
            field=models.PositiveSmallIntegerField(
                help_text=b"Database used to identify literature.",
                choices=[
                    (0, b"External link"),
                    (1, b"PubMed"),
                    (2, b"HERO"),
                    (3, b"RIS (Endnote/Refman)"),
                    (4, b"DOI"),
                    (5, b"Web of Science"),
                    (6, b"Scopus"),
                    (7, b"Embase"),
                ],
            ),
        ),
        migrations.RunPython(
            typeConvertPubmedResultsToStr, reverse_code=typeConvertPubmedResultsToInt
        ),
    ]
