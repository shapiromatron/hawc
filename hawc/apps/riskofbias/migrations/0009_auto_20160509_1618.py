# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-09 21:18


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("riskofbias", "0008_auto_20160428_1208"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="riskofbias",
            options={"ordering": ("final", "id",), "verbose_name_plural": "Risk of Biases"},
        ),
        migrations.RenameField(
            model_name="riskofbias", old_name="conflict_resolution", new_name="final",
        ),
        migrations.AlterField(
            model_name="riskofbias",
            name="active",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
