from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0030_assessment_part1"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="assessment",
            name="public",
        ),
        migrations.RemoveField(
            model_name="assessment",
            name="is_public_training_data",
        ),
    ]
