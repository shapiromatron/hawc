from django.db import migrations, models
from django.db.migrations.operations.special import RunPython
from django.db.models import Count


def set_animal_version(apps, schema_editor):
    # set animal_version to 1 on existing assessments that have animal studies
    Assessment = apps.get_model("assessment", "Assessment")
    Assessment.objects.annotate(n_sp=Count("references__study__experiments")).filter(
        n_sp__gt=0
    ).update(animal_version=1)


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0038_alter_assessmentdetail_qa_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="animal_version",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "v1"), (2, "v2")],
                default=2,
                help_text="Data extraction schema version used for animal studies",
                verbose_name="Animal schema version",
            ),
        ),
        migrations.RunPython(set_animal_version, RunPython.noop),
    ]
