from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0005_auto_20151021_1624"),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name="identifiers",
            index_together=set([("database", "unique_id")]),
        ),
    ]
