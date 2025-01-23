from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0040_dsstox_search_dsstox_dsstox_search_idx"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessment",
            name="vocabulary",
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(1, "EHV"), (2, "ToxRefDB")],
                default=1,
                help_text="Attempt to use a controlled vocabulary for entering bioassay data into HAWC.\n        You still have the option to enter terms which are not available in the vocabulary.",
                null=True,
                verbose_name="Controlled vocabulary",
            ),
        ),
    ]
