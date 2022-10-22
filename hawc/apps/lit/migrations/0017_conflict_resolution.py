import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

from .. import managers


def disable_conflict_resolution(apps, schema_editor):
    # Do not enable conflict resolution on existing apps
    apps.get_model("lit", "LiteratureAssessment").objects.update(conflict_resolution=False)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("lit", "0016_doi_lowercase"),
    ]

    operations = [
        migrations.AddField(
            model_name="literatureassessment",
            name="color_list_1",
            field=models.CharField(
                default="#00ff00",
                help_text="Keywords in list 1 will be highlighted this color",
                max_length=7,
                verbose_name="Highlight Color 1",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="color_list_2",
            field=models.CharField(
                default="#ff0000",
                help_text="Keywords in list 2 will be highlighted this color",
                max_length=7,
                verbose_name="Highlight Color 2",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="color_list_3",
            field=models.CharField(
                default="#0000ff",
                help_text="Keywords in list 3 will be highlighted this color",
                max_length=7,
                verbose_name="Highlight Color 3",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="conflict_resolution",
            field=models.BooleanField(
                default=settings.HAWC_FEATURES.DEFAULT_LITERATURE_CONFLICT_RESOLUTION,
                help_text="Enable conflict resolution for reference screening. If enabled, at least two reviewers must independently review and tag literature, and tag conflicts must be resolved before tags are applied to a reference. If disabled, tags are immediately applied to references.  We do not recommend changing this setting after screening has begun.",
                verbose_name="Conflict resolution required",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="keyword_list_1",
            field=models.TextField(
                blank=True,
                help_text='Keywords to highlight in titles and abstracts on the reference tagging page.\n         Keywords are pipe-separated ("|") to allow for highlighting chemicals which may include\n         commas.',
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="keyword_list_2",
            field=models.TextField(
                blank=True,
                help_text='Keywords to highlight in titles and abstracts on the reference tagging page.\n         Keywords are pipe-separated ("|") to allow for highlighting chemicals which may include\n         commas.',
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="keyword_list_3",
            field=models.TextField(
                blank=True,
                help_text='Keywords to highlight in titles and abstracts on the reference tagging page.\n         Keywords are pipe-separated ("|") to allow for highlighting chemicals which may include\n         commas.',
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="name_list_1",
            field=models.CharField(
                default="Positive",
                help_text="Name for this list of keywords",
                max_length=64,
                verbose_name="Name List 1",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="name_list_2",
            field=models.CharField(
                default="Negative",
                help_text="Name for this list of keywords",
                max_length=64,
                verbose_name="Name List 2",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="name_list_3",
            field=models.CharField(
                default="Additional",
                help_text="Name for this list of keywords",
                max_length=64,
                verbose_name="Name List 3",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="screening_instructions",
            field=models.TextField(
                blank=True,
                help_text="Add instructions for screeners. This information will be shown on the\n        literature screening page and will publicly available, if the assessment is made public.",
            ),
        ),
        migrations.AlterField(
            model_name="literatureassessment",
            name="extraction_tag",
            field=models.ForeignKey(
                blank=True,
                help_text="References tagged with this tag or its descendants will be available for data extraction and study quality/risk of bias evaluation.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="lit.referencefiltertag",
            ),
        ),
        migrations.CreateModel(
            name="UserReferenceTag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reference_tags",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reference",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_tags",
                        to="lit.reference",
                    ),
                ),
                (
                    "tags",
                    managers.ReferenceFilterTagManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="lit.ReferenceTags",
                        to="lit.ReferenceFilterTag",
                        verbose_name="Tags",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(disable_conflict_resolution, reverse_code=migrations.RunPython.noop),
    ]
