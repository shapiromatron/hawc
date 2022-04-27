# Generated by Django 3.2.13 on 2022-04-26 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epiv2", "0012_alter_dataextraction_factors"),
    ]

    operations = [
        migrations.AddField(
            model_name="dataextraction",
            name="exposure_transform",
            field=models.CharField(
                blank=True,
                choices=[
                    ("N/A", "N/A"),
                    ("NR", "NR"),
                    ("log(x+1)", "log(x+1)"),
                    ("log10", "log10"),
                    ("log2", "log2"),
                    ("ln", "ln"),
                    ("log (unspecified basis)", "log (unspecified basis)"),
                    ("z-score", "z-score"),
                    ("squared", "squared"),
                    ("cubic", "cubic"),
                    ("other", "other"),
                ],
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="dataextraction",
            name="outcome_transform",
            field=models.CharField(
                blank=True,
                choices=[
                    ("N/A", "N/A"),
                    ("NR", "NR"),
                    ("log(x+1)", "log(x+1)"),
                    ("log10", "log10"),
                    ("log2", "log2"),
                    ("ln", "ln"),
                    ("log (unspecified basis)", "log (unspecified basis)"),
                    ("z-score", "z-score"),
                    ("squared", "squared"),
                    ("cubic", "cubic"),
                    ("other", "other"),
                ],
                max_length=32,
                null=True,
            ),
        ),
    ]
