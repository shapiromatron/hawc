import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("study", "0001_initial"),
        ("epi", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MetaProtocol",
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
                    models.CharField(max_length=128, verbose_name=b"Protocol name"),
                ),
                (
                    "protocol_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[(0, b"Meta-analysis"), (1, b"Pooled-analysis")],
                    ),
                ),
                (
                    "lit_search_strategy",
                    models.PositiveSmallIntegerField(
                        default=0,
                        verbose_name=b"Literature search strategy",
                        choices=[(0, b"Systematic"), (1, b"Other")],
                    ),
                ),
                (
                    "lit_search_notes",
                    models.TextField(verbose_name=b"Literature search notes", blank=True),
                ),
                (
                    "lit_search_start_date",
                    models.DateField(
                        null=True,
                        verbose_name=b"Literature search start-date",
                        blank=True,
                    ),
                ),
                (
                    "lit_search_end_date",
                    models.DateField(
                        null=True,
                        verbose_name=b"Literature search end-date",
                        blank=True,
                    ),
                ),
                (
                    "total_references",
                    models.PositiveIntegerField(
                        help_text=b"References identified through initial literature-search before application of inclusion/exclusion criteria",
                        null=True,
                        verbose_name=b"Total number of references found",
                        blank=True,
                    ),
                ),
                (
                    "total_studies_identified",
                    models.PositiveIntegerField(
                        help_text=b"Total references identified for inclusion after application of literature review and screening criteria",
                        verbose_name=b"Total number of studies identified",
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "exclusion_criteria",
                    models.ManyToManyField(
                        related_name="meta_exclusion_criteria",
                        to="epi.Criteria",
                        blank=True,
                    ),
                ),
                (
                    "inclusion_criteria",
                    models.ManyToManyField(
                        related_name="meta_inclusion_criteria",
                        to="epi.Criteria",
                        blank=True,
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        related_name="meta_protocols", to="study.Study", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="MetaResult",
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
                ("label", models.CharField(max_length=128)),
                (
                    "data_location",
                    models.CharField(
                        help_text=b"Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)",
                        max_length=128,
                        blank=True,
                    ),
                ),
                ("health_outcome", models.CharField(max_length=128)),
                ("health_outcome_notes", models.TextField(blank=True)),
                ("exposure_name", models.CharField(max_length=128)),
                ("exposure_details", models.TextField(blank=True)),
                ("number_studies", models.PositiveSmallIntegerField()),
                ("statistical_notes", models.TextField(blank=True)),
                (
                    "n",
                    models.PositiveIntegerField(
                        help_text=b"Number of individuals included from all analyses"
                    ),
                ),
                ("estimate", models.FloatField()),
                ("heterogeneity", models.CharField(max_length=256, blank=True)),
                (
                    "lower_ci",
                    models.FloatField(
                        help_text=b"Numerical value for lower-confidence interval",
                        verbose_name=b"Lower CI",
                    ),
                ),
                (
                    "upper_ci",
                    models.FloatField(
                        help_text=b"Numerical value for upper-confidence interval",
                        verbose_name=b"Upper CI",
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
                ("notes", models.TextField(blank=True)),
                (
                    "adjustment_factors",
                    models.ManyToManyField(
                        help_text=b"All factors which were included in final model",
                        related_name="meta_adjustments",
                        to="epi.AdjustmentFactor",
                        blank=True,
                    ),
                ),
                ("metric", models.ForeignKey(to="epi.ResultMetric", on_delete=models.CASCADE)),
                (
                    "protocol",
                    models.ForeignKey(
                        related_name="results", to="epimeta.MetaProtocol", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"ordering": ("label",)},
        ),
        migrations.CreateModel(
            name="SingleResult",
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
                    "exposure_name",
                    models.CharField(
                        help_text=b'Enter a descriptive-name for the single study result (e.g., "Smith et al. 2000, obese-males")',
                        max_length=128,
                    ),
                ),
                (
                    "weight",
                    models.FloatField(
                        blank=True,
                        help_text=b"For meta-analysis, enter the fraction-weight assigned for each result (leave-blank for pooled analyses)",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(1),
                        ],
                    ),
                ),
                (
                    "n",
                    models.PositiveIntegerField(
                        help_text=b"Enter the number of observations for this result",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "estimate",
                    models.FloatField(
                        help_text=b"Enter the numerical risk-estimate presented for this result",
                        null=True,
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
                    "ci_units",
                    models.FloatField(
                        default=0.95,
                        help_text=b"A 95% CI is written as 0.95.",
                        null=True,
                        verbose_name=b"Confidence Interval (CI)",
                        blank=True,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "meta_result",
                    models.ForeignKey(
                        related_name="single_results",
                        to="epimeta.MetaResult",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        related_name="single_results",
                        blank=True,
                        to="study.Study",
                        on_delete=models.SET_NULL,
                        null=True,
                    ),
                ),
            ],
        ),
    ]
