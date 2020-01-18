# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-02 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myuser", "0002_auto_20150629_1327"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="HERO_access",
            field=models.BooleanField(
                default=False,
                help_text="All HERO links will redirect to the login-only HERO access page, allowing for full article text.",
                verbose_name="HERO access",
            ),
        ),
    ]
