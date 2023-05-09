from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0032_assessment_epi_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="admin_notes",
            field=models.TextField(
                blank=True,
                help_text="Additional information about this assessment; only visible to HAWC admins",
            ),
        ),
    ]
