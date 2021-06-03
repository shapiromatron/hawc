from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vocab", "0005_delete_comment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="term", name="uid", field=models.PositiveIntegerField(unique=True),
        ),
    ]
