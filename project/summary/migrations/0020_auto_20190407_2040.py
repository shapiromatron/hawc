# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-08 01:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0019_datapivotupload_worksheet_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="visual",
            name="sort_order",
            field=models.CharField(
                choices=[
                    ("short_citation", "Short Citation"),
                    ("overall_confidence", "Final Study Confidence"),
                ],
                default="short_citation",
                max_length=40,
            ),
        ),
        migrations.AlterField(
            model_name="datapivotupload",
            name="excel_file",
            field=models.FileField(
                help_text="Upload an Excel file in XLSX format.",
                max_length=250,
                upload_to="data_pivot_excel",
                verbose_name="Excel file",
            ),
        ),
        migrations.AlterField(
            model_name="visual",
            name="endpoints",
            field=models.ManyToManyField(
                blank=True,
                help_text="Endpoints to be included in visualization",
                related_name="visuals",
                to="assessment.BaseEndpoint",
            ),
        ),
    ]
