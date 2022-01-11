# Generated by Django 3.2.10 on 2022-01-10 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epiv2", "0005_studypopulation_race"),
    ]

    operations = [
        migrations.AddField(
            model_name="studypopulation",
            name="study_name",
            field=models.CharField(
                blank=True,
                help_text="Typically available for cohorts. Abbreviations provided in the paper are fine",
                max_length=64,
                null=True,
                verbose_name="Study name (if applicable",
            ),
        ),
        migrations.AddField(
            model_name="studypopulation",
            name="years",
            field=models.CharField(
                blank=True, max_length=64, null=True, verbose_name="Year(s) of data collection"
            ),
        ),
    ]
