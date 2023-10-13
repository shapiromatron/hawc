from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0011_auto_20150723_1600"),
    ]

    operations = [
        migrations.AddField(
            model_name="endpoint",
            name="effect_subtype",
            field=models.CharField(
                help_text=b"Effect subtype, using common-vocabulary",
                max_length=128,
                blank=True,
            ),
        ),
    ]
