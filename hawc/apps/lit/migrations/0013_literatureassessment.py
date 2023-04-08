import django
from django.db import migrations, models

from hawc.apps.lit.models import ReferenceFilterTag


def build_lit_assessments(apps, schema_editor):
    Assessment = apps.get_model("assessment", "Assessment")
    LiteratureAssessment = apps.get_model("lit", "LiteratureAssessment")
    for assessment in Assessment.objects.all():
        # adapted  from `LiteratureAssessment.build_default`
        extraction_tag = (
            ReferenceFilterTag.get_assessment_root(assessment.id)
            .get_children()
            .filter(name="Inclusion")
            .first()
        )

        LiteratureAssessment.objects.create(
            assessment=assessment,
            extraction_tag_id=extraction_tag.id if extraction_tag else None,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0015_flavor_options"),
        ("lit", "0012_reference_authors_list"),
    ]

    operations = [
        migrations.CreateModel(
            name="LiteratureAssessment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        editable=False,
                        related_name="literature_settings",
                        to="assessment.Assessment",
                    ),
                ),
                (
                    "extraction_tag",
                    models.ForeignKey(
                        blank=True,
                        help_text="All references or child references of this tag will be marked as ready for extraction.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="lit.ReferenceFilterTag",
                    ),
                ),
            ],
        ),
        migrations.RunPython(build_lit_assessments, reverse_code=migrations.RunPython.noop),
    ]
