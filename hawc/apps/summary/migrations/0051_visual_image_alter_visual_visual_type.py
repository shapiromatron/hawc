# Generated by Django 4.2.6 on 2023-10-21 02:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0050_heatmap_counts"),
    ]

    operations = [
        migrations.AddField(
            model_name="visual",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="summary/visual/images"),
        ),
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
                    (8, "static image"),
                ]
            ),
        ),
    ]
