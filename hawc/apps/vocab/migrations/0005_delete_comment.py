from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("vocab", "0004_term_uid"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Comment",
        ),
    ]
