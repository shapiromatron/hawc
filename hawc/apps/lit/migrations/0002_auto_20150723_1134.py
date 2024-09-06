from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="search",
            options={
                "ordering": ["-last_updated"],
                "get_latest_by": "last_updated",
                "verbose_name_plural": "searches / imports",
            },
        ),
    ]
