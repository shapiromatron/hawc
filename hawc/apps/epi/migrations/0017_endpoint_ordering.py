# Generated by Django 2.2.15 on 2020-08-28 14:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("epi", "0016_exposure_dtxsid"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="outcome",
            options={"ordering": ("id",)},
        ),
        migrations.AlterModelOptions(
            name="result",
            options={"ordering": ("id",)},
        ),
    ]
