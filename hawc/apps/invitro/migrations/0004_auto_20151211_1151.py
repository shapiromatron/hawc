from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invitro", "0003_auto_20150910_1536"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ivexperiment",
            name="serum",
            field=models.CharField(
                help_text=b"Percent serum, serum-type, and/or description",
                max_length=128,
            ),
        ),
    ]
