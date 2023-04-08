# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-23 19:37


from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0016_auto_20160114_1521"),
    ]

    operations = [
        migrations.AddField(
            model_name="endpoint",
            name="expected_adversity_direction",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (3, b"increase from reference/control group"),
                    (2, b"decrease from reference/control group"),
                    (1, b"any change from reference/control group"),
                    (0, b"not reported"),
                ],
                default=0,
                help_text=b"Response direction which would be considered adverse",
                verbose_name=b"Expected response adversity direction",
            ),
        ),
    ]
