# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-28 17:08


from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("riskofbias", "0007_auto_20160426_1536"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="riskofbias",
            options={
                "ordering": ("conflict_resolution",),
                "verbose_name_plural": "Risk of Biases",
            },
        ),
        migrations.AddField(
            model_name="riskofbias", name="active", field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="riskofbias",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="riskofbiases",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
