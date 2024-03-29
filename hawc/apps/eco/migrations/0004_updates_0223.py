# Generated by Django 3.2.16 on 2023-02-02 19:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eco", "0003_updates"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cause",
            name="exposure_value",
            field=models.FloatField(
                blank=True,
                help_text="Specific numeric value of exposure metric reported, if applicable",
                null=True,
                verbose_name="Exposure metric (numeric)",
            ),
        ),
        migrations.AlterField(
            model_name="cause",
            name="level_value",
            field=models.FloatField(
                blank=True,
                help_text="Specific numeric value of treatment/exposure/dose level, if applicable",
                null=True,
                verbose_name="Level (numeric)",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="variability",
            field=models.ForeignKey(
                blank=True,
                help_text="Type of variability reported for the numeric response measure",
                limit_choices_to={"category": 9},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="result_by_variability",
                to="eco.vocab",
                verbose_name="Response variability",
            ),
        ),
    ]
