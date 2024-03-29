# Generated by Django 1.11.15 on 2018-10-29 03:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0018_datapivotupload_excel_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="datapivotupload",
            name="worksheet_name",
            field=models.CharField(
                blank=True,
                help_text="Worksheet name to use in Excel file. If blank, the first worksheet is used.",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="datapivotupload",
            name="excel_file",
            field=models.FileField(
                help_text="Upload an Excel file in XLSX format.",
                upload_to="data_pivot_excel",
                verbose_name="Excel file",
            ),
        ),
    ]
