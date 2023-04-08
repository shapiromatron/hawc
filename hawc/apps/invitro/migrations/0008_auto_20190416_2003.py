# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-17 01:03
from __future__ import unicode_literals

from django.db import migrations, models


def update_choices(apps, schema_editor):
    apps.get_model("invitro", "IVEndpoint").objects.filter(monotonicity=5).update(monotonicity=4)
    apps.get_model("invitro", "IVEndpoint").objects.filter(monotonicity=7).update(monotonicity=6)


class Migration(migrations.Migration):
    dependencies = [
        ("invitro", "0007_py3_unicode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ivendpoint",
            name="monotonicity",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (8, "--"),
                    (0, "N/A, single dose level study"),
                    (1, "N/A, no effects detected"),
                    (2, "visual appearance of monotonicity"),
                    (3, "monotonic and significant trend"),
                    (4, "visual appearance of non-monotonicity"),
                    (6, "no pattern/unclear"),
                ],
                default=8,
            ),
        ),
        migrations.RunPython(update_choices),
    ]
