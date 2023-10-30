from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0003_auto_20150723_1557"),
    ]

    operations = [
        migrations.AddField(
            model_name="datapivotquery",
            name="export_style",
            field=models.PositiveSmallIntegerField(
                default=0,
                choices=[
                    (0, b"One row per Endpoint-group/Result-group"),
                    (1, b"One row per Endpoint/Result"),
                ],
                help_text="The export style changes the level at which the data are aggregated, and therefore which columns and types of data are presented in the export, for use in the visual.",
            ),
        ),
    ]
