# Generated by Django 2.2.15 on 2020-08-28 14:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("invitro", "0009_ivchemical_dtxsid"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="ivendpoint",
            options={"ordering": ("id",)},
        ),
    ]
