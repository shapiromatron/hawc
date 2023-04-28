from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invitro", "0004_auto_20151211_1151"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ivendpoint",
            name="observation_time",
            field=models.CharField(max_length=32, blank=True),
        ),
    ]
