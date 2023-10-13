from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0001_initial"),
        ("assessment", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BMD_Assessment_Settings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "BMDS_version",
                    models.CharField(
                        default=b"2.40",
                        max_length=10,
                        choices=[
                            (b"2.30", b"Version 2.30"),
                            (b"2.31", b"Version 2.31"),
                            (b"2.40", b"Version 2.40"),
                        ],
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.OneToOneField(
                        related_name="BMD_Settings",
                        to="assessment.Assessment",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"verbose_name_plural": "BMD settings"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BMD_model_run",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("model_name", models.CharField(max_length=25)),
                ("option_defaults", models.TextField()),
                ("option_override", models.TextField(blank=True)),
                ("option_override_text", models.TextField(blank=True)),
                ("output_text", models.TextField(blank=True)),
                ("outputs", models.TextField(blank=True)),
                ("d3_plotting", models.TextField(blank=True)),
                ("runtime_error", models.BooleanField(default=False)),
                (
                    "plot",
                    models.ImageField(null=True, upload_to=b"bmds_plot", blank=True),
                ),
                ("option_id", models.PositiveSmallIntegerField()),
                ("bmr_id", models.PositiveSmallIntegerField()),
                ("override", models.PositiveSmallIntegerField(default=99)),
                ("override_text", models.TextField(default=b"")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BMD_session",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "BMDS_version",
                    models.CharField(
                        max_length=10,
                        choices=[
                            (b"2.30", b"Version 2.30"),
                            (b"2.31", b"Version 2.31"),
                            (b"2.40", b"Version 2.40"),
                        ],
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("bmrs", models.TextField(blank=True)),
                ("notes", models.TextField()),
                (
                    "dose_units",
                    models.ForeignKey(to="assessment.DoseUnits", on_delete=models.CASCADE),
                ),
                (
                    "endpoint",
                    models.ForeignKey(
                        related_name="BMD_session",
                        to="animal.Endpoint",
                        on_delete=models.CASCADE,
                        null=True,
                    ),
                ),
                (
                    "selected_model",
                    models.OneToOneField(
                        related_name="selected",
                        on_delete=models.CASCADE,
                        null=True,
                        blank=True,
                        to="bmd.BMD_model_run",
                    ),
                ),
            ],
            options={"get_latest_by": "last_updated"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="LogicField",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("logic_id", models.PositiveSmallIntegerField(editable=False)),
                ("name", models.CharField(max_length=30, editable=False)),
                ("function_name", models.CharField(max_length=25, editable=False)),
                ("description", models.TextField(editable=False)),
                (
                    "failure_bin",
                    models.PositiveSmallIntegerField(
                        help_text=b"If the test fails, select the model-bin should the model be placed into.",
                        choices=[
                            (0, b"Warning (no change)"),
                            (1, b"Questionable"),
                            (2, b"Not Viable"),
                        ],
                    ),
                ),
                (
                    "threshold",
                    models.DecimalField(
                        help_text=b"If a threshold is required for the test, threshold can be specified to non-default.",
                        null=True,
                        max_digits=5,
                        decimal_places=2,
                        blank=True,
                    ),
                ),
                (
                    "continuous_on",
                    models.BooleanField(default=True, verbose_name=b"Continuous Datasets"),
                ),
                (
                    "dichotomous_on",
                    models.BooleanField(default=True, verbose_name=b"Dichotomous Datasets"),
                ),
                (
                    "cancer_dichotomous_on",
                    models.BooleanField(default=True, verbose_name=b"Cancer Dichotomous Datasets"),
                ),
                (
                    "assessment",
                    models.ForeignKey(
                        related_name="BMD_Logic_Fields",
                        editable=False,
                        to="assessment.Assessment",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ["logic_id"]},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="bmd_model_run",
            name="BMD_session",
            field=models.ForeignKey(to="bmd.BMD_session", on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
