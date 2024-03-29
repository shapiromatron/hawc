# Generated by Django 3.2.10 on 2022-01-06 18:59

from django.db import migrations, models
from django.db.migrations.operations.special import RunPython
from django.db.models import Count


def set_epi_version(apps, schema_editor):
    # set epi_version to 1 on existing assessments that have epidemiology studies
    Assessment = apps.get_model("assessment", "Assessment")
    Assessment.objects.annotate(n_sp=Count("references__study__study_populations")).filter(
        n_sp__gt=0
    ).update(epi_version=1)


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0031_assessment_part2"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="epi_version",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "v1"), (2, "v2")],
                default=2,
                verbose_name="Epidemiology schema version",
                help_text="Data extraction schema version used for epidemiology studies",
            ),
        ),
        migrations.RunPython(set_epi_version, RunPython.noop),
    ]
