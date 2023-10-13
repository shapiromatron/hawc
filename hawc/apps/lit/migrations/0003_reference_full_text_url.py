from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0002_auto_20150723_1134"),
    ]

    operations = [
        migrations.AddField(
            model_name="reference",
            name="full_text_url",
            field=models.URLField(
                help_text=b"Link to full-text publication (may require increased access privileges, only reviewers and team-members)",
                blank=True,
            ),
        ),
    ]
