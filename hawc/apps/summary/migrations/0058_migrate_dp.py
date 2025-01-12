import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0047_alter_labeleditem_options"),
        ("summary", "0057_delete_summarytext"),
    ]

    operations = [
        migrations.AddField(
            model_name="visual",
            name="dataset",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="assessment.dataset",
            ),
        ),
        migrations.AddField(
            model_name="visual",
            name="dp_id",
            field=models.BigIntegerField(
                editable=False, blank=True, null=True, help_text="data pivot migration"
            ),
        ),
        migrations.AddField(
            model_name="visual",
            name="dp_slug",
            field=models.SlugField(editable=False, blank=True, help_text="data pivot migration"),
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
                    (9, "PRISMA"),
                    (10, "Data Pivot Query"),
                    (11, "Data Pivot File"),
                ]
            ),
        ),
    ]
