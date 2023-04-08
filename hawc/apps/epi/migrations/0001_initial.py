import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0006_auto_20150724_1151"),
        ("study", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdjustmentFactor",
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
                ("description", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(to="assessment.Assessment", on_delete=models.CASCADE),
                ),
            ],
            options={"ordering": ("description",)},
        ),
        migrations.CreateModel(
            name="ComparisonSet",
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
                ("name", models.CharField(max_length=256)),
                ("description", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Country",
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
                ("code", models.CharField(max_length=2, blank=True)),
                ("name", models.CharField(unique=True, max_length=64)),
            ],
            options={"ordering": ("name",), "verbose_name_plural": "Countries"},
        ),
        migrations.CreateModel(
            name="Criteria",
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
                ("description", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(to="assessment.Assessment", on_delete=models.CASCADE),
                ),
            ],
            options={"ordering": ("description",), "verbose_name_plural": "Criteria"},
        ),
        migrations.CreateModel(
            name="Ethnicity",
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
                ("name", models.CharField(unique=True, max_length=64)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name_plural": "Ethnicities"},
        ),
        migrations.CreateModel(
            name="Exposure",
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
                    "name",
                    models.CharField(
                        help_text=b"Name of exposure and exposure-route", max_length=128
                    ),
                ),
                ("inhalation", models.BooleanField(default=False)),
                ("dermal", models.BooleanField(default=False)),
                ("oral", models.BooleanField(default=False)),
                ("in_utero", models.BooleanField(default=False)),
                (
                    "iv",
                    models.BooleanField(default=False, verbose_name=b"Intravenous (IV)"),
                ),
                ("unknown_route", models.BooleanField(default=False)),
                (
                    "measured",
                    models.CharField(max_length=128, verbose_name=b"What was measured", blank=True),
                ),
                (
                    "metric",
                    models.CharField(max_length=128, verbose_name=b"Measurement Metric"),
                ),
                (
                    "metric_description",
                    models.TextField(verbose_name=b"Measurement Description"),
                ),
                (
                    "analytical_method",
                    models.TextField(
                        help_text=b"Include details on the lab-techniques for exposure measurement in samples."
                    ),
                ),
                (
                    "sampling_period",
                    models.CharField(
                        help_text=b"Exposure sampling period",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "duration",
                    models.CharField(help_text=b"Exposure duration", max_length=128, blank=True),
                ),
                (
                    "exposure_distribution",
                    models.CharField(
                        help_text=b'May be used to describe the exposure distribution, for example, "2.05 \xc2\xb5g/g creatinine (urine), geometric mean; 25th percentile = 1.18, 75th percentile = 3.33"',
                        max_length=128,
                        blank=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "metric_units",
                    models.ForeignKey(to="assessment.DoseUnits", on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("name",),
                "verbose_name": "Exposure",
                "verbose_name_plural": "Exposures",
            },
        ),
        migrations.CreateModel(
            name="Group",
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
                ("group_id", models.PositiveSmallIntegerField()),
                ("name", models.CharField(max_length=256)),
                (
                    "numeric",
                    models.FloatField(
                        help_text=b"Numerical value, can be used for sorting",
                        null=True,
                        verbose_name=b"Numerical value (sorting)",
                        blank=True,
                    ),
                ),
                (
                    "comparative_name",
                    models.CharField(
                        help_text=b'Group and value, displayed in plots, for example "1.5-2.5(Q2) vs \xe2\x89\xa41.5(Q1)", or if only one group is available, "4.8\xc2\xb10.2 (mean\xc2\xb1SEM)"',
                        max_length=64,
                        verbose_name=b"Comparative Name",
                        blank=True,
                    ),
                ),
                (
                    "sex",
                    models.CharField(
                        default=b"U",
                        max_length=1,
                        choices=[
                            (b"U", b"Not reported"),
                            (b"M", b"Male"),
                            (b"F", b"Female"),
                            (b"B", b"Male and Female"),
                        ],
                    ),
                ),
                (
                    "eligible_n",
                    models.PositiveIntegerField(null=True, verbose_name=b"Eligible N", blank=True),
                ),
                (
                    "invited_n",
                    models.PositiveIntegerField(null=True, verbose_name=b"Invited N", blank=True),
                ),
                (
                    "participant_n",
                    models.PositiveIntegerField(
                        null=True, verbose_name=b"Participant N", blank=True
                    ),
                ),
                (
                    "isControl",
                    models.NullBooleanField(
                        default=None,
                        choices=[(True, b"Yes"), (False, b"No"), (None, b"N/A")],
                        help_text=b"Should this group be interpreted as a null/control group",
                        verbose_name=b"Control?",
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        help_text=b"Any other comments related to this group",
                        blank=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "comparison_set",
                    models.ForeignKey(
                        related_name="groups", to="epi.ComparisonSet", on_delete=models.CASCADE
                    ),
                ),
                ("ethnicities", models.ManyToManyField(to="epi.Ethnicity", blank=True)),
            ],
            options={"ordering": ("comparison_set", "group_id")},
        ),
        migrations.CreateModel(
            name="GroupNumericalDescriptions",
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
                    "description",
                    models.CharField(
                        help_text=b"Description if numeric ages do not make sense for this study-population (ex: longitudinal studies)",
                        max_length=128,
                    ),
                ),
                (
                    "mean",
                    models.FloatField(null=True, verbose_name=b"Central estimate", blank=True),
                ),
                (
                    "mean_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name=b"Central estimate type",
                        choices=[
                            (0, None),
                            (1, b"mean"),
                            (2, b"geometric mean"),
                            (3, b"median"),
                            (4, b"other"),
                        ],
                    ),
                ),
                (
                    "is_calculated",
                    models.BooleanField(
                        default=False,
                        help_text=b"Was value calculated/estimated from literature?",
                    ),
                ),
                ("variance", models.FloatField(null=True, blank=True)),
                (
                    "variance_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[(0, None), (1, b"SD"), (2, b"SEM"), (3, b"GSD"), (4, b"other")],
                    ),
                ),
                ("lower", models.FloatField(null=True, blank=True)),
                (
                    "lower_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[(0, None), (1, b"lower limit"), (2, b"5% CI"), (3, b"other")],
                    ),
                ),
                ("upper", models.FloatField(null=True, blank=True)),
                (
                    "upper_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[(0, None), (1, b"upper limit"), (2, b"95% CI"), (3, b"other")],
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        related_name="descriptions", to="epi.Group", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"verbose_name_plural": "Group Numerical Descriptions"},
        ),
        migrations.CreateModel(
            name="GroupResult",
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
                    "n",
                    models.PositiveIntegerField(
                        help_text=b"Individuals in group where outcome was measured",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "estimate",
                    models.FloatField(
                        help_text=b"Central tendency estimate for group",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "variance",
                    models.FloatField(
                        help_text=b"Variance estimate for group",
                        null=True,
                        verbose_name=b"Variance",
                        blank=True,
                    ),
                ),
                (
                    "lower_ci",
                    models.FloatField(
                        help_text=b"Numerical value for lower-confidence interval",
                        null=True,
                        verbose_name=b"Lower CI",
                        blank=True,
                    ),
                ),
                (
                    "upper_ci",
                    models.FloatField(
                        help_text=b"Numerical value for upper-confidence interval",
                        null=True,
                        verbose_name=b"Upper CI",
                        blank=True,
                    ),
                ),
                (
                    "p_value_qualifier",
                    models.CharField(
                        default=b"-",
                        max_length=1,
                        verbose_name=b"p-value qualifier",
                        choices=[
                            (b" ", b"-"),
                            (b"-", b"n.s."),
                            (b"<", b"<"),
                            (b"=", b"="),
                            (b">", b">"),
                        ],
                    ),
                ),
                (
                    "p_value",
                    models.FloatField(
                        blank=True,
                        null=True,
                        verbose_name=b"p-value",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(1.0),
                        ],
                    ),
                ),
                (
                    "is_main_finding",
                    models.BooleanField(
                        help_text=b"Is this the main-finding for this outcome?",
                        verbose_name=b"Main finding",
                    ),
                ),
                (
                    "main_finding_support",
                    models.PositiveSmallIntegerField(
                        default=1,
                        help_text=b"Are the results supportive of the main-finding?",
                        choices=[
                            (3, b"not-reported"),
                            (2, b"supportive"),
                            (1, b"inconclusive"),
                            (0, b"not-supportive"),
                        ],
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "group",
                    models.ForeignKey(
                        related_name="results", to="epi.Group", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"ordering": ("result", "group__comparison_set_id")},
        ),
        migrations.CreateModel(
            name="Outcome",
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
                (
                    "system",
                    models.CharField(
                        help_text=b"Relevant biological system",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "effect",
                    models.CharField(
                        help_text=b"Effect, using common-vocabulary",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "diagnostic",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, b"not reported"),
                            (1, b"medical professional or test"),
                            (2, b"medical records"),
                            (3, b"self-reported"),
                            (4, b"questionnaire"),
                            (5, b"hospital admission"),
                            (6, b"other"),
                        ]
                    ),
                ),
                ("diagnostic_description", models.TextField()),
                (
                    "outcome_n",
                    models.PositiveIntegerField(null=True, verbose_name=b"Outcome N", blank=True),
                ),
                (
                    "summary",
                    models.TextField(
                        help_text=b'Summarize main findings of outcome, or describe why no details are presented (for example, "no association (data not shown)")',
                        blank=True,
                    ),
                ),
            ],
            bases=("assessment.baseendpoint",),
        ),
        migrations.CreateModel(
            name="Result",
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
                    "metric_description",
                    models.TextField(
                        help_text=b"Add additional text describing the metric used, if needed.",
                        blank=True,
                    ),
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
                    "population_description",
                    models.CharField(
                        help_text=b'Detailed description of the population being studied forthis outcome, which may be a subset of the entirestudy-population. For example, "US (national) NHANES2003-2008, Hispanic children 6-18 years, \xe2\x99\x82\xe2\x99\x80 (n=797)"',
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "dose_response",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text=b"Was a trend observed?",
                        verbose_name=b"Dose Response Trend",
                        choices=[
                            (0, b"not-applicable"),
                            (1, b"monotonic"),
                            (2, b"non-monotonic"),
                            (3, b"no trend"),
                            (4, b"not reported"),
                        ],
                    ),
                ),
                ("dose_response_details", models.TextField(blank=True)),
                (
                    "prevalence_incidence",
                    models.CharField(
                        max_length=128,
                        verbose_name=b"Overall incidence prevalence",
                        blank=True,
                    ),
                ),
                (
                    "statistical_power",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text=b"Is the study sufficiently powered?",
                        choices=[
                            (0, b"not reported or calculated"),
                            (1, b"appears to be adequately powered (sample size met)"),
                            (
                                2,
                                b"somewhat underpowered (sample size is 75% to <100% of recommended)",
                            ),
                            (3, b"underpowered (sample size is 50 to <75% required)"),
                            (
                                4,
                                b"severely underpowered (sample size is <50% required)",
                            ),
                        ],
                    ),
                ),
                ("statistical_power_details", models.TextField(blank=True)),
                (
                    "trend_test",
                    models.CharField(
                        help_text="Enter result, if available (ex: p=0.015, p\u22640.05, n.s., etc.)",
                        max_length=128,
                        verbose_name=b"Trend test result",
                        blank=True,
                    ),
                ),
                (
                    "estimate_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name=b"Central estimate type",
                        choices=[
                            (0, None),
                            (1, b"mean"),
                            (2, b"geometric mean"),
                            (3, b"median"),
                            (5, b"point"),
                            (4, b"other"),
                        ],
                    ),
                ),
                (
                    "variance_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[(0, None), (1, b"SD"), (2, b"SEM"), (3, b"GSD"), (4, b"other")],
                    ),
                ),
                (
                    "ci_units",
                    models.FloatField(
                        default=0.95,
                        help_text=b"A 95% CI is written as 0.95.",
                        null=True,
                        verbose_name=b"Confidence Interval (CI)",
                        blank=True,
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        help_text=b'Summarize main findings of outcome, or describe why no details are presented (for example, "no association (data not shown)")',
                        blank=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="ResultAdjustmentFactor",
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
                ("included_in_final_model", models.BooleanField(default=True)),
                (
                    "adjustment_factor",
                    models.ForeignKey(
                        related_name="resfactors",
                        to="epi.AdjustmentFactor",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "result",
                    models.ForeignKey(
                        related_name="resfactors", to="epi.Result", on_delete=models.CASCADE
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ResultMetric",
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
                ("metric", models.CharField(unique=True, max_length=128)),
                ("abbreviation", models.CharField(max_length=32)),
                (
                    "isLog",
                    models.BooleanField(
                        default=True,
                        help_text=b"When plotting, use a log base 10 scale",
                        verbose_name=b"Display as log",
                    ),
                ),
                (
                    "showForestPlot",
                    models.BooleanField(
                        default=True,
                        help_text=b"Does forest-plot representation of result make sense?",
                        verbose_name=b"Show on forest plot",
                    ),
                ),
                (
                    "reference_value",
                    models.FloatField(
                        default=1,
                        help_text=b"Null hypothesis value for reference, if applicable",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "order",
                    models.PositiveSmallIntegerField(
                        help_text=b"Order as they appear in option-list"
                    ),
                ),
            ],
            options={"ordering": ("order",)},
        ),
        migrations.CreateModel(
            name="StudyPopulation",
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
                ("name", models.CharField(max_length=256)),
                (
                    "design",
                    models.CharField(
                        max_length=2,
                        choices=[
                            (b"CO", b"Cohort"),
                            (b"CX", b"Cohort (Retrospective)"),
                            (b"CY", b"Cohort (Prospective)"),
                            (b"CC", b"Case-control"),
                            (b"NC", b"Nested case-control"),
                            (b"CR", b"Case report"),
                            (b"SE", b"Case series"),
                            (b"CT", b"Controlled trial"),
                            (b"CS", b"Cross-sectional"),
                        ],
                    ),
                ),
                (
                    "age_profile",
                    models.CharField(
                        help_text=b"Age profile of population (ex: adults, children, pregnant women, etc.)",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        help_text=b"Population source (ex: general population, environmental exposure, occupational cohort)",
                        max_length=128,
                        blank=True,
                    ),
                ),
                ("region", models.CharField(max_length=128, blank=True)),
                ("state", models.CharField(max_length=128, blank=True)),
                (
                    "eligible_n",
                    models.PositiveIntegerField(null=True, verbose_name=b"Eligible N", blank=True),
                ),
                (
                    "invited_n",
                    models.PositiveIntegerField(null=True, verbose_name=b"Invited N", blank=True),
                ),
                (
                    "participant_n",
                    models.PositiveIntegerField(
                        null=True, verbose_name=b"Participant N", blank=True
                    ),
                ),
                (
                    "comments",
                    models.TextField(help_text=b"Note matching criteria, etc.", blank=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("country", models.ForeignKey(to="epi.Country", on_delete=models.CASCADE)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="StudyPopulationCriteria",
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
                    "criteria_type",
                    models.CharField(
                        max_length=1,
                        choices=[
                            (b"I", b"Inclusion"),
                            (b"E", b"Exclusion"),
                            (b"C", b"Confounding"),
                        ],
                    ),
                ),
                (
                    "criteria",
                    models.ForeignKey(
                        related_name="spcriteria", to="epi.Criteria", on_delete=models.CASCADE
                    ),
                ),
                (
                    "study_population",
                    models.ForeignKey(
                        related_name="spcriteria",
                        to="epi.StudyPopulation",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="studypopulation",
            name="criteria",
            field=models.ManyToManyField(
                related_name="populations",
                through="epi.StudyPopulationCriteria",
                to="epi.Criteria",
            ),
        ),
        migrations.AddField(
            model_name="studypopulation",
            name="study",
            field=models.ForeignKey(
                related_name="study_populations", to="study.Study", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="result",
            name="adjustment_factors",
            field=models.ManyToManyField(
                related_name="outcomes",
                through="epi.ResultAdjustmentFactor",
                to="epi.AdjustmentFactor",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="result",
            name="comparison_set",
            field=models.ForeignKey(
                related_name="results", to="epi.ComparisonSet", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="result",
            name="metric",
            field=models.ForeignKey(
                related_name="results",
                to="epi.ResultMetric",
                on_delete=models.CASCADE,
                help_text=b"&nbsp;",
            ),
        ),
        migrations.AddField(
            model_name="result",
            name="outcome",
            field=models.ForeignKey(
                related_name="results", to="epi.Outcome", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="outcome",
            name="study_population",
            field=models.ForeignKey(
                related_name="outcomes", to="epi.StudyPopulation", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="groupresult",
            name="result",
            field=models.ForeignKey(
                related_name="results", to="epi.Result", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="Exposure",
            name="study_population",
            field=models.ForeignKey(
                related_name="exposures", to="epi.StudyPopulation", on_delete=models.CASCADE
            ),
        ),
        migrations.AddField(
            model_name="comparisonset",
            name="exposure",
            field=models.ForeignKey(
                related_name="comparison_sets",
                on_delete=models.CASCADE,
                blank=True,
                to="epi.Exposure",
                help_text=b"Exposure-group associated with this group",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="comparisonset",
            name="outcome",
            field=models.ForeignKey(
                related_name="comparison_sets",
                to="epi.Outcome",
                on_delete=models.SET_NULL,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="comparisonset",
            name="study_population",
            field=models.ForeignKey(
                related_name="comparison_sets",
                to="epi.StudyPopulation",
                on_delete=models.SET_NULL,
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="criteria",
            unique_together=set([("assessment", "description")]),
        ),
        migrations.AlterUniqueTogether(
            name="adjustmentfactor",
            unique_together=set([("assessment", "description")]),
        ),
    ]
