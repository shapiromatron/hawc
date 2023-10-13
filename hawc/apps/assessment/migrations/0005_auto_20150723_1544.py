from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0004_auto_20150723_1530"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="strain",
            unique_together=set([("species", "name")]),
        ),
    ]
