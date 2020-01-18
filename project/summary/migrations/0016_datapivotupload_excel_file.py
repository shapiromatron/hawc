# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-28 03:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0015_endpoint_and_py3_unicode"),
    ]

    operations = [
        migrations.AddField(
            model_name="datapivotupload",
            name="excel_file",
            field=models.FileField(
                blank=True,
                help_text="Upload an Excel file (XLSX). If the file contains multiple worksheets (tabs), the data from the first worksheet will be used.",
                null=True,
                upload_to="data_pivot_excel",
                verbose_name="Excel file",
            ),
        ),
    ]
