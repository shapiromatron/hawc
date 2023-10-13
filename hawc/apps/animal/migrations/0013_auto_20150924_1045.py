from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0012_endpoint_effect_subtype"),
    ]

    operations = [
        migrations.AlterField(
            model_name="endpoint",
            name="observation_time_units",
            field=models.PositiveSmallIntegerField(
                default=0,
                choices=[
                    (0, b"not-reported"),
                    (1, b"seconds"),
                    (2, b"minutes"),
                    (3, b"hours"),
                    (4, b"days"),
                    (5, b"weeks"),
                    (6, b"months"),
                    (9, b"years"),
                    (7, b"PND"),
                    (8, b"GD"),
                ],
            ),
        ),
    ]
