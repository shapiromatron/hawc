from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("epimeta", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="singleresult",
            options={"ordering": ("exposure_name",)},
        ),
    ]
