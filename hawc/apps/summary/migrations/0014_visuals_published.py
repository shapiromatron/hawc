# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-29 12:56
from __future__ import unicode_literals

from django.db import migrations, models


def make_public(apps, schema_editor):
    Models = [
        apps.get_model("summary", "Visual"),
        apps.get_model("summary", "DataPivot"),
    ]
    for Model in Models:
        Model.objects.all().update(published=True)


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0013_optional_captions"),
    ]

    operations = [
        migrations.AddField(
            model_name="datapivot",
            name="published",
            field=models.BooleanField(
                default=False,
                help_text="For assessments marked for public viewing, mark visual to be viewable by public",
                verbose_name="Publish visual for public viewing",
            ),
        ),
        migrations.AddField(
            model_name="visual",
            name="published",
            field=models.BooleanField(
                default=False,
                help_text="For assessments marked for public viewing, mark visual to be viewable by public",
                verbose_name="Publish visual for public viewing",
            ),
        ),
        migrations.RunPython(make_public, reverse_code=migrations.RunPython.noop),
    ]
