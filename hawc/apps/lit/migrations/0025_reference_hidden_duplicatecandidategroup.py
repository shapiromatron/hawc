# Generated by Django 5.1.4 on 2025-02-13 12:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0047_alter_labeleditem_options"),
        ("lit", "0024_workflows"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="reference",
            name="hidden",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="DuplicateCandidateGroup",
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
                    "resolution",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Unresolved"),
                            (1, "Primary identified"),
                            (2, "False positive"),
                        ],
                        default=0,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="duplicates",
                        to="assessment.assessment",
                    ),
                ),
                (
                    "candidates",
                    models.ManyToManyField(related_name="duplicate_candidates", to="lit.reference"),
                ),
                (
                    "primary",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="duplicate_primaries",
                        to="lit.reference",
                    ),
                ),
                (
                    "resolving_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="resolved_duplicates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
