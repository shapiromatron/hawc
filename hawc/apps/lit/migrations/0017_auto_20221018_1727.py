# Generated by Django 3.2.15 on 2022-10-18 21:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import hawc.apps.lit.managers
from hawc.constants import FeatureFlags


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
                blank=True,
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
                blank=True,
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
                blank=True,
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
                default=False,
                help_text="Enable conflict resolution for reference screening. TODO: ADD FURTHER HELP TEXT",
                verbose_name="Conflict Resolution",
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
                blank=True,
                default="Positive",
                help_text="Name for this list of keywords",
                max_length=128,
                verbose_name="Name List 1",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="name_list_2",
            field=models.CharField(
                blank=True,
                default="Negative",
                help_text="Name for this list of keywords",
                max_length=128,
                verbose_name="Name List 2",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="name_list_3",
            field=models.CharField(
                blank=True,
                default="Additional",
                help_text="Name for this list of keywords",
                max_length=128,
                verbose_name="Name List 3",
            ),
        ),
        migrations.AddField(
            model_name="literatureassessment",
            name="screening_instructions",
            field=models.TextField(
                blank=True,
                help_text="Add instructions for screeners. This information will be shown on the\n        literature screening page and will never be made public.",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "reference",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lit_userreferencetag_items",
                        to="lit.reference",
                    ),
                ),
                (
                    "tags",
                    hawc.apps.lit.managers.ReferenceFilterTagManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="lit.ReferenceTags",
                        to="lit.ReferenceFilterTag",
                        verbose_name="Tags",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lit_userreferencetag_items",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="literatureassessment",
            name="conflict_resolution",
            field=models.BooleanField(
                default=FeatureFlags.from_env("HAWC_FEATURE_FLAGS").DEFAULT_CONFLICT_RES,
                help_text="Enable conflict resolution for reference screening. TODO: ADD FURTHER HELP TEXT",
                verbose_name="Conflict Resolution",
            ),
        ),
    ]
