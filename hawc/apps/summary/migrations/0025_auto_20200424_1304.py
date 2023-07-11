# Generated by Django 2.2.11 on 2020-04-24 17:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0024_add_external_websites"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visual",
            name="visual_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "animal bioassay endpoint aggregation"),
                    (1, "animal bioassay endpoint crossview"),
                    (2, "risk of bias heatmap"),
                    (3, "risk of bias barchart"),
                    (4, "literature tagtree"),
                    (5, "embedded external website"),
                    (6, "exploratory heatmap"),
                    (7, "plotly"),
                ]
            ),
        ),
    ]
