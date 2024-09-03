from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0005_auto_20151021_1624"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="identifiers",
            index=models.Index(
                fields=["database", "unique_id"], name="lit_identif_databas_394ab9_idx"
            ),
        ),
    ]
