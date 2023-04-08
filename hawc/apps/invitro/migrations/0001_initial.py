import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0001_initial"),
        ("assessment", "0001_initial"),
        ("study", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="IVBenchmark",
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
                ("benchmark", models.CharField(max_length=32)),
                ("value", models.FloatField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IVCellType",
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
                ("species", models.CharField(max_length=64)),
                ("strain", models.CharField(default=b"not applicable", max_length=64)),
                (
                    "sex",
                    models.CharField(
                        max_length=2,
                        choices=[
                            (b"m", b"Male"),
                            (b"f", b"Female"),
                            (b"mf", b"Male and female"),
                            (b"na", b"Not-applicable"),
                            (b"nr", b"Not-reported"),
                        ],
                    ),
                ),
                ("cell_type", models.CharField(max_length=64)),
                ("tissue", models.CharField(max_length=64)),
                (
                    "source",
                    models.CharField(max_length=128, verbose_name=b"Source of cell cultures"),
                ),
                (
                    "study",
                    models.ForeignKey(
                        related_name="ivcelltypes", to="study.Study", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IVChemical",
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
                ("name", models.CharField(max_length=128)),
                (
                    "cas",
                    models.CharField(
                        max_length=40,
                        verbose_name=b"Chemical identifier (CAS)",
                        blank=True,
                    ),
                ),
                (
                    "cas_inferred",
                    models.BooleanField(
                        default=False,
                        help_text=b"Was the correct CAS inferred or incorrect in the original document?",
                        verbose_name=b"CAS inferred?",
                    ),
                ),
                (
                    "cas_notes",
                    models.CharField(max_length=256, verbose_name=b"CAS determination notes"),
                ),
                (
                    "source",
                    models.CharField(max_length=128, verbose_name=b"Source of chemical"),
                ),
                (
                    "purity",
                    models.CharField(
                        help_text=b"Ex: >99%, not-reported, etc.",
                        max_length=32,
                        verbose_name=b"Chemical purity",
                    ),
                ),
                (
                    "purity_confirmed",
                    models.BooleanField(
                        default=False, verbose_name=b"Purity experimentally confirmed"
                    ),
                ),
                ("purity_confirmed_notes", models.TextField(blank=True)),
                (
                    "dilution_storage_notes",
                    models.TextField(
                        help_text=b"Dilution, storage, and observations such as precipitation should be noted here."
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        related_name="ivchemicals", to="study.Study", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IVEndpoint",
            fields=[
                (
                    "baseendpoint_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="assessment.BaseEndpoint",
                        on_delete=models.CASCADE,
                    ),
                ),
                ("assay_type", models.CharField(max_length=128)),
                (
                    "short_description",
                    models.CharField(
                        help_text=b"Short (<128 character) description of effect & measurement",
                        max_length=128,
                    ),
                ),
                (
                    "effect",
                    models.CharField(help_text=b"Effect, using common-vocabulary", max_length=128),
                ),
                (
                    "data_location",
                    models.CharField(
                        help_text=b"Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "data_type",
                    models.CharField(
                        default=b"C",
                        max_length=2,
                        verbose_name=b"Dataset type",
                        choices=[
                            (b"C", b"Continuous"),
                            (b"D", b"Dichotomous"),
                            (b"NR", b"Not reported"),
                        ],
                    ),
                ),
                (
                    "variance_type",
                    models.PositiveSmallIntegerField(
                        default=0, choices=[(0, b"NA"), (1, b"SD"), (2, b"SE")]
                    ),
                ),
                (
                    "response_units",
                    models.CharField(max_length=64, verbose_name=b"Response units"),
                ),
                ("observation_time", models.FloatField(default=-999)),
                (
                    "observation_time_units",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[
                            (0, b"not-reported"),
                            (1, b"seconds"),
                            (2, b"minutes"),
                            (3, b"hours"),
                            (4, b"days"),
                            (5, b"weeks"),
                            (6, b"months"),
                        ],
                    ),
                ),
                (
                    "NOEL",
                    models.SmallIntegerField(
                        default=-999,
                        help_text=b"No observed effect level",
                        verbose_name=b"NOEL",
                    ),
                ),
                (
                    "LOEL",
                    models.SmallIntegerField(
                        default=-999,
                        help_text=b"Lowest observed effect level",
                        verbose_name=b"LOEL",
                    ),
                ),
                (
                    "monotonicity",
                    models.PositiveSmallIntegerField(
                        default=8,
                        choices=[
                            (0, b"N/A, single dose level study"),
                            (1, b"N/A, no effects detected"),
                            (2, b"yes, visual appearance of monotonicity but no trend"),
                            (3, b"yes, monotonic and significant trend"),
                            (
                                4,
                                b"yes, visual appearance of non-monotonic but no trend",
                            ),
                            (5, b"yes, non-monotonic and significant trend"),
                            (6, b"no pattern"),
                            (7, b"unclear"),
                            (8, b"not-reported"),
                        ],
                    ),
                ),
                (
                    "overall_pattern",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[
                            (0, b"not-available"),
                            (1, b"increase"),
                            (2, b"increase, then decrease"),
                            (6, b"increase, then no change"),
                            (3, b"decrease"),
                            (4, b"decrease, then increase"),
                            (7, b"decrease, then no change"),
                            (5, b"no clear pattern"),
                        ],
                    ),
                ),
                (
                    "statistical_test_notes",
                    models.CharField(
                        help_text=b"Notes describing details on the statistical tests performed",
                        max_length=256,
                        blank=True,
                    ),
                ),
                (
                    "trend_test",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[
                            (0, b"not-reported"),
                            (1, b"not-analyzed"),
                            (2, b"not-applicable"),
                            (3, b"significant"),
                            (4, b"not-significant"),
                        ],
                    ),
                ),
                (
                    "trend_test_notes",
                    models.CharField(
                        help_text=b"Notes describing details on the trend-test performed",
                        max_length=256,
                        blank=True,
                    ),
                ),
                (
                    "endpoint_notes",
                    models.TextField(
                        help_text=b"Any additional notes regarding the endpoint itself",
                        blank=True,
                    ),
                ),
                (
                    "result_notes",
                    models.TextField(
                        help_text=b"Qualitative description of the results", blank=True
                    ),
                ),
                ("additional_fields", models.TextField(default=b"{}")),
            ],
            options={},
            bases=("assessment.baseendpoint",),
        ),
        migrations.CreateModel(
            name="IVEndpointCategory",
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
                ("path", models.CharField(unique=True, max_length=255)),
                ("depth", models.PositiveIntegerField()),
                ("numchild", models.PositiveIntegerField(default=0)),
                ("name", models.CharField(max_length=128)),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IVEndpointGroup",
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
                ("dose_group_id", models.PositiveSmallIntegerField()),
                (
                    "dose",
                    models.FloatField(validators=[django.core.validators.MinValueValidator(0)]),
                ),
                (
                    "n",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                ("response", models.FloatField(null=True, blank=True)),
                (
                    "variance",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "difference_control",
                    models.CharField(
                        default=b"nc",
                        max_length=2,
                        choices=[
                            (b"nc", b"no-change"),
                            (b"-", b"decrease"),
                            (b"+", b"increase"),
                            (b"nt", b"not-tested"),
                        ],
                    ),
                ),
                (
                    "significant_control",
                    models.CharField(
                        default=b"nr",
                        max_length=2,
                        choices=[
                            (b"nr", "not reported"),
                            (b"si", "p \u2264 0.05"),
                            (b"ns", "not significant"),
                            (b"na", "not applicable"),
                        ],
                    ),
                ),
                (
                    "cytotoxicity_observed",
                    models.NullBooleanField(
                        default=None,
                        choices=[
                            (None, b"not reported"),
                            (False, b"not observed"),
                            (True, b"observed"),
                        ],
                    ),
                ),
                (
                    "precipitation_observed",
                    models.NullBooleanField(
                        default=None,
                        choices=[
                            (None, b"not reported"),
                            (False, b"not observed"),
                            (True, b"observed"),
                        ],
                    ),
                ),
                (
                    "endpoint",
                    models.ForeignKey(
                        related_name="groups", to="invitro.IVEndpoint", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"ordering": ("endpoint", "dose_group_id")},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IVExperiment",
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
                    "transfection",
                    models.CharField(
                        help_text=b'Details on transfection methodology and details on genes or other genetic material introduced into assay, or "not-applicable"',
                        max_length=256,
                    ),
                ),
                (
                    "cell_line",
                    models.CharField(
                        help_text=b"Description of type of cell-line used (ex: primary cell-line, immortalized cell-line, stably transfected cell-line, transient transfected cell-line, etc.)",
                        max_length=128,
                    ),
                ),
                (
                    "dosing_notes",
                    models.TextField(
                        help_text=b"Notes describing dosing-protocol, including duration-details",
                        blank=True,
                    ),
                ),
                (
                    "metabolic_activation",
                    models.CharField(
                        default=b"nr",
                        help_text=b"Was metabolic-activation used in system (ex: S9)?",
                        max_length=2,
                        choices=[
                            (b"+", b"with metabolic activation"),
                            (b"-", b"without metabolic activation"),
                            (b"na", b"not applicable"),
                            (b"nr", b"not reported"),
                        ],
                    ),
                ),
                (
                    "serum",
                    models.CharField(
                        max_length=128,
                        verbose_name=b"Percent serum, serum-type, and/or description",
                    ),
                ),
                ("has_positive_control", models.BooleanField(default=False)),
                (
                    "positive_control",
                    models.CharField(
                        help_text=b"Positive control chemical or other notes",
                        max_length=128,
                        blank=True,
                    ),
                ),
                ("has_negative_control", models.BooleanField(default=False)),
                (
                    "negative_control",
                    models.CharField(
                        help_text=b"Negative control chemical or other notes",
                        max_length=128,
                        blank=True,
                    ),
                ),
                ("has_vehicle_control", models.BooleanField(default=False)),
                (
                    "vehicle_control",
                    models.CharField(
                        help_text=b"Vehicle control chemical or other notes",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "control_notes",
                    models.CharField(
                        help_text=b"Additional details related to controls",
                        max_length=256,
                        blank=True,
                    ),
                ),
                (
                    "cell_type",
                    models.ForeignKey(
                        related_name="ivexperiments",
                        to="invitro.IVCellType",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "dose_units",
                    models.ForeignKey(
                        related_name="ivexperiments",
                        to="assessment.DoseUnits",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        related_name="ivexperiments", to="study.Study", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="ivendpoint",
            name="category",
            field=models.ForeignKey(
                related_name="endpoints",
                blank=True,
                to="invitro.IVEndpointCategory",
                null=True,
                on_delete=models.SET_NULL,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ivendpoint",
            name="chemical",
            field=models.ForeignKey(
                related_name="endpoints", to="invitro.IVChemical", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ivendpoint",
            name="experiment",
            field=models.ForeignKey(
                related_name="endpoints", to="invitro.IVExperiment", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="ivbenchmark",
            name="endpoint",
            field=models.ForeignKey(
                related_name="benchmarks", to="invitro.IVEndpoint", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
