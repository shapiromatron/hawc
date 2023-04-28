from django.db import migrations, models

from hawc.apps.common import validators


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0040_tableau_filters"),
    ]

    operations = [
        migrations.AddField(
            model_name="summarytable",
            name="caption",
            field=models.TextField(
                blank=True,
                validators=[
                    validators.validate_html_tags,
                    validators.validate_hyperlinks,
                ],
            ),
        ),
    ]
