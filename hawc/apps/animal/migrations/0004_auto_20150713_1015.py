import django.core.validators
from django.db import migrations, models


def setPurityQualifier(apps, schema_editor):
    apps.get_model("animal", "Experiment").objects.filter(purity__isnull=False).update(
        purity_qualifier="\u2265"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0003_auto_20150629_1327"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiment",
            name="purity_qualifier",
            field=models.CharField(
                default="",
                max_length=1,
                choices=[(">", ">"), ("\u2265", "\u2265"), ("=", "="), ("", "")],
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="purity",
            field=models.FloatField(
                blank=True,
                help_text=b"Percentage value (ex: 95%)",
                null=True,
                verbose_name=b"Chemical purity (%)",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
            ),
        ),
        migrations.RunPython(setPurityQualifier, reverse_code=migrations.RunPython.noop),
    ]
