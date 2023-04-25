from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("epi", "0002_load_fixtures"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="groupresult",
            options={"ordering": ("result", "group__group_id")},
        ),
    ]
