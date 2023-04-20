from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0002_auto_20150629_1327"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="assessment",
            name="enable_reference_values",
        ),
    ]
