# Generated by Django 5.1.4 on 2025-02-05 17:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lit", "0025_dedupesettings_duplicatecandidates"),
    ]

    operations = [
        migrations.AddField(
            model_name="reference",
            name="hidden",
            field=models.BooleanField(default=False),
        ),
    ]
