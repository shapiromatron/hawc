# Generated by Django 3.2.12 on 2022-02-23 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epiv2", "0003_alter_exposure_measurement_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exposure",
            name="biomonitoring_matrix",
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
