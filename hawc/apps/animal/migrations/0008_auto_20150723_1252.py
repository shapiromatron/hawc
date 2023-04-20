from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0007_auto_20150723_1202"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="individualanimal",
            name="endpoint_group",
        ),
        migrations.RemoveField(
            model_name="endpoint",
            name="individual_animal_data",
        ),
        migrations.DeleteModel(
            name="IndividualAnimal",
        ),
    ]
