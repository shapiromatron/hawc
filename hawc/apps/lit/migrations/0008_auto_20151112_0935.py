from django.db import migrations

from ...common.models import CustomURLField


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0007_auto_20151103_0925"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reference",
            name="full_text_url",
            field=CustomURLField(
                help_text=b"Link to full-text publication (may require increased access privileges, only reviewers and team-members)",
                blank=True,
            ),
        ),
    ]
