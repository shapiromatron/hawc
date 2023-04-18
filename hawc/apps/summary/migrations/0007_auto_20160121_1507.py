from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0006_remove_datapivotquery_units"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="datapivotquery",
            name="units",
        ),
    ]
