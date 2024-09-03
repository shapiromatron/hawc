# Generated by Django 4.2.7 on 2023-11-30 20:25

import django.db.models.deletion
from django.db import migrations, models

import hawc.apps.lit.managers


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0037_delete_blog"),
        ("lit", "0023_referencetags_reference_tag_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Workflow",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="Descriptive name for this workflow.", max_length=32
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="A description or set of notes for for this workflow.",
                    ),
                ),
                (
                    "link_tagging",
                    models.BooleanField(
                        default=False,
                        help_text="Add a panel on the Literature Review page for tagging references in this workflow.",
                    ),
                ),
                (
                    "link_conflict_resolution",
                    models.BooleanField(
                        default=False,
                        help_text="Add a panel on the Literature Review page for resolving conflicts on references in this workflow.",
                    ),
                ),
                (
                    "admission_tags_descendants",
                    models.BooleanField(
                        default=False,
                        help_text="Applies to tags selected above. By default, only references with the exact\n          selected tag(s) are admitted to the workflow; checking this box includes references that\n            are tagged with any descendant of the selected tag(s).",
                    ),
                ),
                (
                    "removal_tags_descendants",
                    models.BooleanField(
                        default=False,
                        help_text="Applies to tags selected above. By default, only references with the exact\n          selected tag(s) are admitted to the workflow; checking this box includes references that\n            are tagged with any descendant of the selected tag(s).",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "admission_source",
                    models.ManyToManyField(
                        blank=True, related_name="workflow_admissions", to="lit.search"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WorkflowRemovalTags",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="lit.workflow"
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workflow_removals",
                        to="lit.referencefiltertag",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="WorkflowAdmissionTags",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="lit.workflow"
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workflow_admissions",
                        to="lit.referencefiltertag",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="workflow",
            name="admission_tags",
            field=hawc.apps.lit.managers.ReferenceFilterTagManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="lit.WorkflowAdmissionTags",
                to="lit.ReferenceFilterTag",
                verbose_name="Tags",
            ),
        ),
        migrations.AddField(
            model_name="workflow",
            name="assessment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="workflows",
                to="assessment.assessment",
            ),
        ),
        migrations.AddField(
            model_name="workflow",
            name="removal_source",
            field=models.ManyToManyField(
                blank=True, related_name="workflow_removals", to="lit.search"
            ),
        ),
        migrations.AddField(
            model_name="workflow",
            name="removal_tags",
            field=hawc.apps.lit.managers.ReferenceFilterTagManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="lit.WorkflowRemovalTags",
                to="lit.ReferenceFilterTag",
                verbose_name="Tags",
            ),
        ),
    ]
