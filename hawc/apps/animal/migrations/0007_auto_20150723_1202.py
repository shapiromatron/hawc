from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0006_auto_20150723_1141"),
    ]

    operations = [
        migrations.AlterField(
            model_name="endpointgroup",
            name="endpoint",
            field=models.ForeignKey(
                related_name="groups", to="animal.Endpoint", on_delete=models.CASCADE
            ),
        ),
    ]
