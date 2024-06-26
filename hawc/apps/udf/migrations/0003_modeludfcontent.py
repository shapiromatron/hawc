# Generated by Django 4.2.4 on 2023-09-27 20:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("udf", "0002_tagbinding_modelbinding"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModelUDFContent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("object_id", models.PositiveIntegerField(null=True)),
                ("content", models.JSONField(default=dict)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype"
                    ),
                ),
                (
                    "model_binding",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_contents",
                        to="udf.modelbinding",
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="modeludfcontent",
            unique_together={("model_binding", "content_type", "object_id")},
        ),
    ]
