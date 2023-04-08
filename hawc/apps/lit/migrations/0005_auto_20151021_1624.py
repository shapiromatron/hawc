from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0004_auto_20151021_1345"),
    ]

    operations = [
        migrations.AlterField(
            model_name="identifiers",
            name="unique_id",
            field=models.CharField(max_length=32, db_index=True),
        ),
    ]
