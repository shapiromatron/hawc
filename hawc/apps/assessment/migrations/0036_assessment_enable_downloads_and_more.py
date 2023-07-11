# Generated by Django 4.2.1 on 2023-05-11 01:25

from datetime import timedelta

from django.db import migrations, models
from django.db.models import Count
from django.utils.timezone import now


def fwd(apps, schema_editor):
    # disable links if no data of that type and hasn't been updated for 6 months.
    qs = apps.get_model("assessment", "Assessment").objects.filter(
        last_updated__lt=now() - timedelta(weeks=26)
    )
    qs.annotate(n_tables=Count("summarytable")).filter(n_tables=0).update(
        enable_summary_tables=False
    )
    qs.annotate(n_visuals=Count("visuals") + Count("datapivot")).filter(n_visuals=0).update(
        enable_visuals=False
    )
    qs.annotate(n_text=Count("summarytext")).filter(n_text__lte=1).update(enable_summary_text=False)


class Migration(migrations.Migration):
    dependencies = [("assessment", "0035_update_assessmentvalue"), ("summary", "0028_summarytable")]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="enable_downloads",
            field=models.BooleanField(
                default=True, help_text="Show the downloads link on the assessment sidebar."
            ),
        ),
        migrations.AddField(
            model_name="assessment",
            name="enable_summary_tables",
            field=models.BooleanField(
                default=True,
                help_text="Create summary tables of data and/or study evaluations extracted in HAWC, or build custom user defined tables. Show the summary tables link on the assessment sidebar.",
            ),
        ),
        migrations.AddField(
            model_name="assessment",
            name="enable_visuals",
            field=models.BooleanField(
                default=True,
                help_text="Create visualizations of data and/or study evaluations extracted in HAWC, or using data uploaded from a tabular dataset. Show the visuals link on the assessment sidebar.",
            ),
        ),
        migrations.RunPython(fwd, migrations.RunPython.noop),
    ]
