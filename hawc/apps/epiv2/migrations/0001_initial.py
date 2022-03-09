import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("study", "0011_auto_20190416_2035"),
        ("assessment", "0032_assessment_epi_version"),
        ("epi", "0018_django31"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdjustmentFactor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="A unique name for this adjustment factor that will help you identify it later.",
                        max_length=64,
                    ),
                ),
                (
                    "description",
                    models.CharField(blank=True, help_text="Comma separated list", max_length=128),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Chemical",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Design",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "study_design",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("CO", "Cohort"),
                            ("CC", "Case-control"),
                            ("NC", "Nested case-control"),
                            ("CR", "Case report"),
                            ("SE", "Case series"),
                            ("RT", "Randomized controlled trial"),
                            ("NT", "Non-randomized controlled trial"),
                            ("CS", "Cross-sectional"),
                            ("OT", "Other"),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("GP", "General population"),
                            ("OC", "Occupational"),
                            ("OT", "Other"),
                        ],
                        max_length=128,
                    ),
                ),
                (
                    "age_profile",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("AD", "Adults"),
                                ("CH", "Children and adolescents <18 yrs"),
                                ("PW", "Pregnant women"),
                                ("OT", "Other"),
                            ],
                            max_length=2,
                        ),
                        blank=True,
                        help_text='Select all that apply. Note: do not select "Pregnant women" if pregnant women are only included as part of a general population sample',
                        size=None,
                        verbose_name="Population age category",
                    ),
                ),
                (
                    "age_description",
                    models.CharField(
                        blank=True, max_length=64, verbose_name="Population age details"
                    ),
                ),
                (
                    "sex",
                    models.CharField(
                        choices=[
                            ("U", "Not reported"),
                            ("M", "Male"),
                            ("F", "Female"),
                            ("B", "Male and Female"),
                        ],
                        default="U",
                        max_length=1,
                    ),
                ),
                (
                    "race",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Population race/ethnicity"
                    ),
                ),
                (
                    "summary",
                    models.CharField(
                        help_text="Breifly describe the study population (e.g., Women undergoing fertility treatment).",
                        max_length=128,
                        verbose_name="Population Summary",
                    ),
                ),
                (
                    "study_name",
                    models.CharField(
                        blank=True,
                        help_text="Typically available for cohorts. Abbreviations provided in the paper are fine",
                        max_length=64,
                        null=True,
                        verbose_name="Study name (if applicable)",
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Other geographic information"
                    ),
                ),
                (
                    "years",
                    models.CharField(
                        blank=True, max_length=64, verbose_name="Year(s) of data collection"
                    ),
                ),
                (
                    "participant_n",
                    models.PositiveIntegerField(
                        help_text="Enter the total number of participants enrolled in the study (after exclusions).\nNote: Sample size for specific result can be extracted in qualitative data extraction",
                        verbose_name="Overall study population N",
                    ),
                ),
                ("criteria", models.TextField(blank=True)),
                ("comments", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("countries", models.ManyToManyField(blank=True, to="epi.Country")),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="designs",
                        to="study.study",
                    ),
                ),
            ],
            options={
                "verbose_name": "Study Population",
                "verbose_name_plural": "Study Populations",
            },
        ),
        migrations.CreateModel(
            name="Exposure",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="A unique name for this exposure that will help you identify it later.",
                        max_length=64,
                    ),
                ),
                (
                    "measurement_type",
                    models.CharField(
                        choices=[
                            ("BM", "Biomonitoring"),
                            ("AR", "Air"),
                            ("FD", "Food"),
                            ("DW", "Drinking water"),
                            ("OC", "Occupational"),
                            ("MD", "Modeled"),
                            ("QN", "Questionnaire"),
                            ("DO", "Direct administration - oral"),
                            ("DI", "Direct administration - inhalation"),
                            ("OT", "Other"),
                        ],
                        max_length=2,
                        verbose_name="Exposure measurement type",
                    ),
                ),
                (
                    "biomonitoring_matrix",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("BL_PLASMA", "Blood (portion: Plasma)"),
                            ("BL_WHOLE", "Blood (portion: Whole blood)"),
                            ("BL_SERUM", "Blood (portion: Serum)"),
                            ("UR", "Urine"),
                            ("TE", "Teeth"),
                            ("NL", "Nails"),
                            ("SA", "Saliva"),
                            ("BM", "Breast milk"),
                            ("SE", "Semen"),
                            ("FC", "Feces"),
                            ("CF", "Cerebrospinal fluid"),
                            ("EB", "Exhaled breath"),
                            ("OT", "Other"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "biomonitoring_source",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("PT", "From participant"),
                            ("ML", "Maternal"),
                            ("PL", "Paternal"),
                            ("CD", "Cord"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "measurement_timing",
                    models.CharField(
                        blank=True,
                        help_text='If timing is based on something other than age, specify the timing (e.g., start of employment at Factory A). If cross-sectional, enter "cross-sectional"',
                        max_length=128,
                        verbose_name="Timing of exposure measurement",
                    ),
                ),
                (
                    "exposure_route",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("IH", "Inhalation"),
                            ("OR", "Oral"),
                            ("DE", "Dermal"),
                            ("IU", "In utero"),
                            ("IV", "Intravenous"),
                            ("UK", "Unknown/Total"),
                        ],
                        max_length=2,
                    ),
                ),
                ("analytic_method", models.CharField(blank=True, max_length=128)),
                ("comments", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "design",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exposures",
                        to="epiv2.design",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Outcome",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "endpoint",
                    models.CharField(
                        help_text="A unique name for this health outcome that will help you identify it later.",
                        max_length=64,
                    ),
                ),
                ("health_outcome", models.CharField(max_length=128)),
                (
                    "health_outcome_system",
                    models.CharField(
                        choices=[
                            ("CA", "Cancer"),
                            ("CV", "Cardiovascular"),
                            ("DE", "Dermal"),
                            ("DV", "Developmental"),
                            ("EN", "Endocrine"),
                            ("GI", "Gastrointestinal"),
                            ("HM", "Hematologic"),
                            ("HP", "Hepatic"),
                            ("IM", "Immune"),
                            ("MT", "Metabolic"),
                            ("MS", "Multi-System"),
                            ("MU", "Musculoskeletal"),
                            ("NV", "Nervous"),
                            ("OC", "Ocular"),
                            ("RP", "Reproductive"),
                            ("RS", "Respiratory"),
                            ("UR", "Urinary"),
                            ("WB", "Whole Body"),
                            ("OT", "Other"),
                        ],
                        help_text="If multiple cancer types are present, report all types under Cancer.",
                        max_length=128,
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "design",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outcomes",
                        to="epiv2.design",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExposureLevel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="A unique name for this exposure level that will help you identify it later.",
                        max_length=64,
                    ),
                ),
                (
                    "sub_population",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Sub-population (if relevant)"
                    ),
                ),
                ("median", models.FloatField(blank=True, null=True)),
                ("mean", models.FloatField(blank=True, null=True)),
                ("units", models.CharField(blank=True, max_length=128, null=True)),
                (
                    "neg_exposure",
                    models.FloatField(
                        blank=True,
                        help_text="e.g., % below the LOD",
                        null=True,
                        verbose_name="Percent with negligible exposure",
                    ),
                ),
                ("lower", models.FloatField(blank=True, null=True)),
                ("percentile25", models.FloatField(blank=True, null=True)),
                ("percentile75", models.FloatField(blank=True, null=True)),
                ("upper", models.FloatField(blank=True, null=True)),
                (
                    "ultype",
                    models.CharField(
                        blank=True,
                        choices=[("MX", "Min/Max"), ("N5", "5/95"), ("N9", "1/99")],
                        default="MX",
                        max_length=128,
                        verbose_name="Upper/lower type",
                    ),
                ),
                ("comments", models.TextField(blank=True, verbose_name="Exposure level comments")),
                (
                    "data_location",
                    models.CharField(blank=True, help_text="e.g., table number", max_length=128),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "chemical",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="epiv2.chemical"
                    ),
                ),
                (
                    "design",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exposure_levels",
                        to="epiv2.design",
                    ),
                ),
                (
                    "exposure_measurement",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="epiv2.exposure",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DataExtraction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "sub_population",
                    models.CharField(
                        blank=True,
                        help_text="Use N/A if sub population is not relevant",
                        max_length=64,
                    ),
                ),
                ("outcome_measurement_timing", models.CharField(blank=True, max_length=128)),
                ("n", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "effect_estimate_type",
                    models.CharField(
                        choices=[
                            ("OR", "Odds Ratio (OR)"),
                            ("RR", "Relative Risk Ratio (RR)"),
                            ("AR", "Absolute Risk %"),
                            ("B", "Regression coeffcient (β)"),
                            ("SMR", "Standardized Mortality Ratio (SMR)"),
                            ("SIR", "Standardized Incidence Ratio (SIR)"),
                            ("IRR", "Incidence Risk Ratio (IRR)"),
                            ("ARR", "Absolute Risk Reduction/ Risk difference (ARR or RD)"),
                            ("HR", "Hazard Ratio (HR)"),
                            ("CM", "Comparison of Means"),
                            ("SCC", "Spearman's Correlation Coefficient"),
                            ("PC", "Percent change"),
                            ("MD", "Mean difference"),
                        ],
                        max_length=3,
                    ),
                ),
                (
                    "effect_description",
                    models.CharField(
                        blank=True,
                        help_text="Description of the effect estimate with units, including comparison group if applicable",
                        max_length=128,
                        verbose_name="Effect estimate description",
                    ),
                ),
                ("effect_estimate", models.FloatField()),
                (
                    "ci_lcl",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Confidence Interval LCL"
                    ),
                ),
                (
                    "ci_ucl",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Confidence Interval UCL"
                    ),
                ),
                (
                    "exposure_rank",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Rank this comparison group by exposure (lowest exposure group = 1)",
                    ),
                ),
                (
                    "sd_or_se",
                    models.FloatField(
                        blank=True, null=True, verbose_name="Standard Deviation or Standard Error"
                    ),
                ),
                ("pvalue", models.CharField(blank=True, max_length=128, verbose_name="p-value")),
                (
                    "significant",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "No"), (1, "Yes"), (2, "N/A")],
                        default=2,
                        verbose_name="Statistically Significant",
                    ),
                ),
                (
                    "confidence",
                    models.CharField(blank=True, max_length=128, verbose_name="Study confidence"),
                ),
                (
                    "data_location",
                    models.CharField(blank=True, help_text="e.g., table number", max_length=128),
                ),
                ("statistical_method", models.TextField(blank=True)),
                ("comments", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "adjustment_factor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="epiv2.adjustmentfactor",
                    ),
                ),
                (
                    "design",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_extractions",
                        to="epiv2.design",
                    ),
                ),
                (
                    "exposure_level",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exposure_levels",
                        to="epiv2.exposurelevel",
                    ),
                ),
                (
                    "outcome",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outcomes",
                        to="epiv2.outcome",
                    ),
                ),
            ],
            options={"verbose_name": "Quantitative data extraction",},
        ),
        migrations.AddField(
            model_name="chemical",
            name="design",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="chemicals",
                to="epiv2.design",
            ),
        ),
        migrations.AddField(
            model_name="chemical",
            name="dsstox",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="assessment.dsstox",
                verbose_name="DSSTox substance identifier",
            ),
        ),
        migrations.AddField(
            model_name="adjustmentfactor",
            name="design",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="adjustment_factors",
                to="epiv2.design",
            ),
        ),
    ]
