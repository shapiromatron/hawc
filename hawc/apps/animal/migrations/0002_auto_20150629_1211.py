import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="endpoint",
            name="data_type",
            field=models.CharField(
                default=b"C",
                max_length=2,
                verbose_name=b"Dataset type",
                choices=[
                    (b"C", b"Continuous"),
                    (b"D", b"Dichotomous"),
                    (b"P", b"Percent Difference"),
                    (b"DC", b"Dichotomous Cancer"),
                    (b"NR", b"Not reported"),
                ],
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="variance_type",
            field=models.PositiveSmallIntegerField(
                default=1, choices=[(0, b"NA"), (1, b"SD"), (2, b"SE"), (3, b"NR")]
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="endpointgroup",
            name="significance_level",
            field=models.FloatField(
                default=None,
                null=True,
                verbose_name=b"Statistical significance level",
                blank=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(1),
                ],
            ),
            preserve_default=True,
        ),
    ]
