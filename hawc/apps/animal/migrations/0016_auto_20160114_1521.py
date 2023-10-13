from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0015_auto_20151218_1348"),
    ]

    operations = [
        migrations.AlterField(
            model_name="endpoint",
            name="response_units",
            field=models.CharField(
                help_text="Units the response was measured in (i.e., \u03bcg/dL, % control, etc.)",
                max_length=32,
                verbose_name=b"Response units",
                blank=True,
            ),
        ),
    ]
