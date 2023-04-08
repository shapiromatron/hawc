from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("invitro", "0005_auto_20151218_1348"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ivendpoint",
            name="response_units",
            field=models.CharField(max_length=64, verbose_name=b"Response units", blank=True),
        ),
    ]
