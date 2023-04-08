import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0004_auto_20150713_1015"),
    ]

    operations = [
        migrations.AlterField(
            model_name="experiment",
            name="purity",
            field=models.FloatField(
                blank=True,
                help_text=b"Percentage (ex: 95%)",
                null=True,
                verbose_name=b"Chemical purity (%)",
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="purity_qualifier",
            field=models.CharField(
                default="",
                max_length=1,
                blank=True,
                choices=[(">", ">"), ("\u2265", "\u2265"), ("=", "="), ("", "")],
            ),
        ),
    ]
