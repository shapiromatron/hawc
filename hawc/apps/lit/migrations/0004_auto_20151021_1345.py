from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0003_reference_full_text_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="search",
            name="import_file",
            field=models.FileField(upload_to=b"lit-search-import", blank=True),
        ),
        migrations.AlterField(
            model_name="identifiers",
            name="database",
            field=models.IntegerField(
                choices=[
                    (0, b"External link"),
                    (1, b"PubMed"),
                    (2, b"HERO"),
                    (3, b"RIS (Endnote/Refman)"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="search",
            name="search_string",
            field=models.TextField(
                help_text=b"The search-text used to query an online database. Use colors to separate search-terms (optional).",
                blank=True,
            ),
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
                ],
            ),
        ),
    ]
