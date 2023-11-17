import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0004_datapivotquery_export_format"),
    ]

    operations = [
        migrations.AddField(
            model_name="datapivotquery",
            name="preferred_units",
            field=django.contrib.postgres.fields.ArrayField(
                default=list,
                help_text=b"List of preferred dose-values, in order of preference. If empty, dose-units will be random for each endpoint presented. This setting may used for comparing percent-response, where dose-units are not needed, or for creating one plot similar, but not identical, dose-units.",
                base_field=models.PositiveIntegerField(),
                size=None,
            ),
        ),
    ]
