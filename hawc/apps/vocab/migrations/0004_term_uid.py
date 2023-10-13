from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vocab", "0003_load_v1"),
    ]

    operations = [
        migrations.AddField(
            model_name="term",
            name="uid",
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
    ]
