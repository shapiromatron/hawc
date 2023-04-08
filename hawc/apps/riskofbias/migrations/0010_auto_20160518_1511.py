# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-18 20:11


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("riskofbias", "0009_auto_20160509_1618"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="riskofbiasscore",
            options={"ordering": ("metric", "id")},
        ),
        migrations.AlterField(
            model_name="riskofbias",
            name="final",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
