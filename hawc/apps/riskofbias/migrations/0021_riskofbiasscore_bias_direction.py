# Generated by Django 2.2.11 on 2020-04-08 02:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("riskofbias", "0020_rob_overrides"),
    ]

    operations = [
        migrations.AddField(
            model_name="riskofbiasscore",
            name="bias_direction",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not entered/unknown"),
                    (1, "⬆ (away from null)"),
                    (2, "⬇ (towards null)"),
                ],
                default=0,
                help_text="Judgment of direction of bias (⬆ = away from null, ⬇ = towards null); only add entry if important to show in visuals",
            ),
        ),
    ]
