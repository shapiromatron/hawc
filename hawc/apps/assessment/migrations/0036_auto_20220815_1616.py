# Generated by Django 3.2.15 on 2022-08-15 21:16

from django.db import migrations, models

import hawc.apps.assessment.constants


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0035_alter_values_value"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessmentdetails",
            name="extra_metadata",
            field=models.JSONField(
                blank=True, default=hawc.apps.assessment.constants.default_metadata
            ),
        ),
        migrations.AlterField(
            model_name="values",
            name="extra_metadata",
            field=models.JSONField(
                blank=True, default=hawc.apps.assessment.constants.default_metadata
            ),
        ),
    ]
