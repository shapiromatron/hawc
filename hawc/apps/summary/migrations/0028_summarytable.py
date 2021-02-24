# Generated by Django 3.1.3 on 2021-01-26 15:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0024_django31"),
        ("summary", "0027_tagtree_hide_empty_tag_nodes"),
    ]

    operations = [
        migrations.CreateModel(
            name="SummaryTable",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=128)),
                (
                    "slug",
                    models.SlugField(
                        help_text="The URL (web address) used to describe this object (no spaces or special-characters).",
                        verbose_name="URL Name",
                    ),
                ),
                ("content", models.JSONField(default=dict)),
                (
                    "table_type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "Generic"), (1, "Evidence Profile")], default=0,
                    ),
                ),
                (
                    "published",
                    models.BooleanField(
                        default=False,
                        help_text="For assessments marked for public viewing, mark table to be viewable by public",
                        verbose_name="Publish table for public viewing",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="assessment.assessment"
                    ),
                ),
            ],
            options={"unique_together": {("assessment", "slug"), ("assessment", "title")}},
        ),
    ]
