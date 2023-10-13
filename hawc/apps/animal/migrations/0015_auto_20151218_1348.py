from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0014_endpoint_observation_time_text"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dosingregime",
            name="route_of_exposure",
            field=models.CharField(
                help_text=b"Primary route of exposure. If multiple primary-exposures, describe in notes-field below",
                max_length=2,
                choices=[
                    (b"OR", "Oral"),
                    (b"OC", "Oral capsule"),
                    (b"OD", "Oral diet"),
                    (b"OG", "Oral gavage"),
                    (b"OW", "Oral drinking water"),
                    (b"I", "Inhalation"),
                    (b"D", "Dermal"),
                    (b"SI", "Subcutaneous injection"),
                    (b"IP", "Intraperitoneal injection"),
                    (b"IV", "Intravenous injection"),
                    (b"IO", "in ovo"),
                    (b"P", "Parental"),
                    (b"W", "Whole body"),
                    (b"M", "Multiple"),
                    (b"U", "Unknown"),
                    (b"O", "Other"),
                ],
            ),
        ),
    ]
