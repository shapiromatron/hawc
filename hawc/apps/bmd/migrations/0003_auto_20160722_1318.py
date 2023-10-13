# Generated by Django 1.9.4 on 2016-07-22 18:18


import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


def updateAssessmentVersion(apps, schema_editor):
    apps.get_model("bmd", "assessmentsettings").objects.all().update(version="BMDS2601")


def undoAssessmentVersion(apps, schema_editor):
    apps.get_model("bmd", "assessmentsettings").objects.all().update(version="2.40")


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0018_auto_20160602_1007"),
        ("assessment", "0007_auto_20160426_1124"),
        ("bmd", "0002_auto_20150723_1557"),
    ]

    operations = [
        # assessment changes
        migrations.RenameModel(old_name="BMD_Assessment_Settings", new_name="AssessmentSettings"),
        migrations.RenameField(
            model_name="AssessmentSettings",
            old_name="BMDS_version",
            new_name="version",
        ),
        migrations.AlterField(
            model_name="assessmentsettings",
            name="assessment",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bmd_settings",
                to="assessment.Assessment",
            ),
        ),
        migrations.AlterField(
            model_name="assessmentsettings",
            name="version",
            field=models.CharField(
                choices=[
                    (b"BMDS230", b"BMDS v2.3.0"),
                    (b"BMDS231", b"BMDS v2.3.1"),
                    (b"BMDS240", b"BMDS v2.4.0"),
                    (b"BMDS260", b"BMDS v2.6.0"),
                    (b"BMDS2601", b"BMDS v2.6.0.1"),
                ],
                default=b"BMDS2601",
                max_length=10,
            ),
        ),
        migrations.RunPython(updateAssessmentVersion, reverse_code=undoAssessmentVersion),
        # logic changes
        migrations.RemoveField(
            model_name="logicfield",
            name="function_name",
        ),
        migrations.RemoveField(
            model_name="logicfield",
            name="logic_id",
        ),
        migrations.AlterField(
            model_name="logicfield",
            name="assessment",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bmd_logic_fields",
                to="assessment.Assessment",
            ),
        ),
        migrations.AlterModelOptions(
            name="logicfield",
            options={"ordering": ("id",)},
        ),
        # session changes
        migrations.CreateModel(
            name="Session",
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
                    "version",
                    models.CharField(
                        choices=[
                            (b"BMDS230", b"BMDS v2.3.0"),
                            (b"BMDS231", b"BMDS v2.3.1"),
                            (b"BMDS240", b"BMDS v2.4.0"),
                            (b"BMDS260", b"BMDS v2.6.0"),
                            (b"BMDS2601", b"BMDS v2.6.0.1"),
                        ],
                        max_length=10,
                    ),
                ),
                ("bmrs", django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ("date_executed", models.DateTimeField(null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "dose_units",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bmd_sessions",
                        to="assessment.DoseUnits",
                    ),
                ),
                (
                    "endpoint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bmd_sessions",
                        to="animal.Endpoint",
                    ),
                ),
            ],
            options={
                "ordering": ("-last_updated",),
                "get_latest_by": "last_updated",
                "verbose_name_plural": "BMD sessions",
            },
        ),
        migrations.RemoveField(
            model_name="bmd_session",
            name="dose_units",
        ),
        migrations.RemoveField(
            model_name="bmd_session",
            name="endpoint",
        ),
        migrations.RemoveField(
            model_name="bmd_session",
            name="selected_model",
        ),
        migrations.RemoveField(
            model_name="bmd_model_run",
            name="BMD_session",
        ),
        migrations.DeleteModel(
            name="BMD_session",
        ),
        # model settings
        migrations.CreateModel(
            name="Model",
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
                ("model_id", models.PositiveSmallIntegerField()),
                ("bmr_id", models.PositiveSmallIntegerField()),
                ("name", models.CharField(max_length=25)),
                (
                    "overrides",
                    django.contrib.postgres.fields.jsonb.JSONField(default=dict),
                ),
                ("date_executed", models.DateTimeField(null=True)),
                ("execution_error", models.BooleanField(default=False)),
                ("dfile", models.TextField(blank=True)),
                ("outfile", models.TextField(blank=True)),
                (
                    "output",
                    django.contrib.postgres.fields.jsonb.JSONField(default=dict),
                ),
                ("plot", models.ImageField(blank=True, upload_to=b"bmds_plot")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="models",
                        to="bmd.Session",
                    ),
                ),
            ],
            options={"ordering": ("model_id", "bmr_id"), "get_latest_by": "created"},
        ),
        migrations.DeleteModel(
            name="BMD_model_run",
        ),
        # selected model
        migrations.CreateModel(
            name="SelectedModel",
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
                ("notes", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "endpoint",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bmd_model",
                        to="animal.Endpoint",
                    ),
                ),
                (
                    "model",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bmd.Model",
                    ),
                ),
            ],
            options={"get_latest_by": "created"},
        ),
    ]
