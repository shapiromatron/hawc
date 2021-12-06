# Generated by Django 2.2.14 on 2020-08-12 13:21

import django.db.models.deletion
from django.db import migrations, models

import hawc.apps.vocab.constants


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Entity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("ontology", models.PositiveSmallIntegerField(choices=[(1, "umls")])),
                ("uid", models.CharField(max_length=128, verbose_name="UID")),
                ("deprecated_on", models.DateTimeField(blank=True, null=True)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name_plural": "entities", "ordering": ("id",)},
        ),
        migrations.CreateModel(
            name="Term",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "namespace",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "EHV")],
                        default=hawc.apps.vocab.constants.VocabularyNamespace(1),
                    ),
                ),
                (
                    "type",
                    models.PositiveIntegerField(
                        choices=[
                            (1, "system"),
                            (2, "organ"),
                            (3, "effect"),
                            (4, "effect_subtype"),
                            (5, "endpoint_name"),
                        ]
                    ),
                ),
                ("name", models.CharField(max_length=256)),
                ("notes", models.TextField(blank=True)),
                ("deprecated_on", models.DateTimeField(blank=True, null=True)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vocab.Term",
                    ),
                ),
            ],
            options={"ordering": ("id",)},
        ),
        migrations.CreateModel(
            name="EntityTermRelation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("deprecated_on", models.DateTimeField(blank=True, null=True)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "entity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="vocab.Entity"
                    ),
                ),
                (
                    "term",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="vocab.Term"),
                ),
            ],
            options={"ordering": ("id",)},
        ),
        migrations.AddField(
            model_name="entity",
            name="terms",
            field=models.ManyToManyField(
                related_name="entities", through="vocab.EntityTermRelation", to="vocab.Term"
            ),
        ),
        migrations.AlterUniqueTogether(name="entity", unique_together={("ontology", "uid")},),
    ]
