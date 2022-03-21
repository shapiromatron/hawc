# Generated by Django 3.1.2 on 2020-10-15 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bmd", "0005_py3_unicode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="model",
            name="output",
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="model",
            name="overrides",
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name="session",
            name="bmrs",
            field=models.JSONField(default=list),
        ),
    ]
