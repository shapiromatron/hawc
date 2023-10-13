import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0001_initial"),
        ("study", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Aggregation",
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
                ("name", models.CharField(max_length=100)),
                (
                    "aggregation_type",
                    models.CharField(
                        default=b"E",
                        help_text=b"The purpose for creating this aggregation.",
                        max_length=2,
                        choices=[
                            (b"E", b"Evidence"),
                            (b"M", b"Mode-of-action"),
                            (b"CD", b"Candidate Reference Values"),
                        ],
                    ),
                ),
                ("summary_text", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        related_name="aggregation",
                        to="assessment.Assessment",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AnimalGroup",
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
                        help_text=b"Short description of the animals (i.e. Male Fischer F344 rats, Female C57BL/6 mice)",
                        max_length=80,
                    ),
                ),
                (
                    "sex",
                    models.CharField(
                        max_length=1,
                        choices=[
                            (b"M", b"Male"),
                            (b"F", b"Female"),
                            (b"C", b"Combined"),
                            (b"R", b"Not reported"),
                        ],
                    ),
                ),
                (
                    "animal_source",
                    models.CharField(
                        help_text=b"Laboratory and/or breeding details where animals were acquired",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "lifestage_exposed",
                    models.CharField(
                        help_text=b'Textual life-stage description when exposure occurred (examples include: "parental, PND18, juvenile, adult, continuous, multiple")',
                        max_length=32,
                        blank=True,
                    ),
                ),
                (
                    "lifestage_assessed",
                    models.CharField(
                        help_text=b'Textual life-stage description when endpoints were measured (examples include: "parental, PND18, juvenile, adult, multiple")',
                        max_length=32,
                        blank=True,
                    ),
                ),
                (
                    "duration_observation",
                    models.FloatField(
                        help_text=b"Numeric length of observation period, in days (fractions allowed)",
                        null=True,
                        verbose_name=b"Observation duration (days)",
                        blank=True,
                    ),
                ),
                (
                    "generation",
                    models.CharField(
                        default=b"",
                        max_length=2,
                        blank=True,
                        choices=[
                            (b"", b"N/A (not generational-study)"),
                            (b"P0", b"Parent-generation (P0)"),
                            (b"F1", b"First-generation (F1)"),
                            (b"F2", b"Second-generation (F2)"),
                            (b"F3", b"Third-generation (F3)"),
                            (b"F4", b"Fourth-generation (F4)"),
                            (b"Ot", b"Other"),
                        ],
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        help_text=b"Any addition notes for this animal-group.",
                        verbose_name=b"Description",
                        blank=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DoseGroup",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("dose_units", "dose_group_id")},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DoseUnits",
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
                ("units", models.CharField(unique=True, max_length=20)),
                ("administered", models.BooleanField(default=False)),
                ("converted", models.BooleanField(default=False)),
                (
                    "hed",
                    models.BooleanField(default=False, verbose_name=b"Human Equivalent Dose"),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name_plural": "dose units"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DosingRegime",
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
                    "route_of_exposure",
                    models.CharField(
                        help_text=b"Primary route of exposure. If multiple primary-exposures, describe in notes-field below",
                        max_length=2,
                        choices=[
                            (b"OC", "Oral capsule"),
                            (b"OD", "Oral diet"),
                            (b"OG", "Oral gavage"),
                            (b"OW", "Oral drinking water"),
                            (b"I", "Inhalation"),
                            (b"D", "Dermal"),
                            (b"SI", "Subcutaneous injection"),
                            (b"IP", "Intraperitoneal injection"),
                            (b"IV", "Intravenous injection"),
                            (b"IO", "in ovo"),
                            (b"P", "Parental"),
                            (b"W", "Whole body"),
                            (b"M", "Multiple"),
                            (b"U", "Unknown"),
                            (b"O", "Other"),
                        ],
                    ),
                ),
                (
                    "duration_exposure",
                    models.FloatField(
                        help_text=b"Length of exposure period (fractions allowed), used for sorting in visualizations",
                        null=True,
                        verbose_name=b"Exposure duration (days)",
                        blank=True,
                    ),
                ),
                (
                    "duration_exposure_text",
                    models.CharField(
                        help_text=b"Text-description of the exposure duration (ex: 21 days, 104 wks, GD0 to PND9, GD0 to weaning)",
                        max_length=128,
                        verbose_name=b"Exposure duration (text)",
                        blank=True,
                    ),
                ),
                (
                    "num_dose_groups",
                    models.PositiveSmallIntegerField(
                        default=4,
                        help_text=b"Number of dose groups, plus control",
                        verbose_name=b"Number of Dose Groups",
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "positive_control",
                    models.NullBooleanField(
                        default=None,
                        help_text=b"Was a positive control used?",
                        choices=[(True, b"Yes"), (False, b"No"), (None, b"Unknown")],
                    ),
                ),
                (
                    "negative_control",
                    models.CharField(
                        default=b"NR",
                        help_text=b"Description of negative-controls used",
                        max_length=2,
                        choices=[
                            (b"NR", b"Not-reported"),
                            (b"UN", b"Untreated"),
                            (b"VT", b"Vehicle-treated"),
                            (b"B", b"Untreated + Vehicle-treated"),
                            (b"Y", b"Yes (untreated and/or vehicle)"),
                            (b"N", b"No"),
                        ],
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text=b"Detailed description of dosing methodology (i.e. exposed via inhalation 5 days/week for 6 hours)",
                        blank=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "dosed_animals",
                    models.OneToOneField(
                        related_name="dosed_animals",
                        null=True,
                        blank=True,
                        to="animal.AnimalGroup",
                        on_delete=models.SET_NULL,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Endpoint",
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
                    "organ",
                    models.CharField(
                        help_text=b"Relevant organ; also include tissue if relevant",
                        max_length=128,
                        verbose_name=b"Organ (and tissue)",
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
                    "observation_time",
                    models.FloatField(
                        help_text=b"Numeric value of the time an observation was reported; optional, should be recorded if the same effect was measured multiple times.",
                        null=True,
                        blank=True,
                    ),
                ),
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
                            (7, b"PND"),
                            (8, b"GD"),
                        ],
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
                    "response_units",
                    models.CharField(
                        help_text="Units the response was measured in (i.e., \u03bcg/dL, % control, etc.)",
                        max_length=32,
                        verbose_name=b"Response units",
                    ),
                ),
                (
                    "data_type",
                    models.CharField(
                        default=b"D",
                        max_length=2,
                        verbose_name=b"Dataset type",
                        choices=[
                            (b"C", b"Continuous"),
                            (b"D", b"Dichotomous"),
                            (b"P", b"Percent Difference"),
                            (b"DC", b"Dichotomous Cancer"),
                            (b"NR", b"Not reported"),
                        ],
                    ),
                ),
                (
                    "variance_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[(0, b"NA"), (1, b"SD"), (2, b"SE"), (3, b"NR")],
                    ),
                ),
                (
                    "confidence_interval",
                    models.FloatField(
                        help_text=b"A 95% CI is written as 0.95.",
                        null=True,
                        verbose_name=b"Confidence interval (CI)",
                        blank=True,
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
                    "FEL",
                    models.SmallIntegerField(
                        default=-999,
                        help_text=b"Frank effect level",
                        verbose_name=b"FEL",
                    ),
                ),
                (
                    "data_reported",
                    models.BooleanField(
                        default=True,
                        help_text=b"Dose-response data for endpoint are available in the literature source",
                    ),
                ),
                (
                    "data_extracted",
                    models.BooleanField(
                        default=True,
                        help_text=b"Dose-response data for endpoint are extracted from literature into HAWC",
                    ),
                ),
                (
                    "values_estimated",
                    models.BooleanField(
                        default=False,
                        help_text=b"Response values were estimated using a digital ruler or other methods",
                    ),
                ),
                (
                    "individual_animal_data",
                    models.BooleanField(
                        default=False,
                        help_text=b"If individual response data are available for each animal.",
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
                    "statistical_test",
                    models.CharField(
                        help_text=b"Description of statistical analysis techniques used",
                        max_length=256,
                        blank=True,
                    ),
                ),
                (
                    "trend_value",
                    models.FloatField(
                        help_text=b"Numerical result for trend-test, if available",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "trend_result",
                    models.PositiveSmallIntegerField(
                        default=3,
                        choices=[
                            (0, b"not applicable"),
                            (1, b"not significant"),
                            (2, b"significant"),
                            (3, b"not reported"),
                        ],
                    ),
                ),
                (
                    "diagnostic",
                    models.TextField(
                        help_text=b"Diagnostic or method used to measure endpoint (if relevant)",
                        blank=True,
                    ),
                ),
                (
                    "power_notes",
                    models.TextField(
                        help_text=b"Power of study-design to detect change from control",
                        blank=True,
                    ),
                ),
                (
                    "results_notes",
                    models.TextField(
                        help_text=b"Qualitative description of the results", blank=True
                    ),
                ),
                (
                    "endpoint_notes",
                    models.TextField(
                        help_text=b"Any additional notes related to this endpoint/methodology, not including results",
                        verbose_name=b"General notes/methodology",
                        blank=True,
                    ),
                ),
                ("additional_fields", models.TextField(default=b"{}")),
                (
                    "animal_group",
                    models.ForeignKey(
                        related_name="endpoints", to="animal.AnimalGroup", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=("assessment.baseendpoint",),
        ),
        migrations.CreateModel(
            name="EndpointGroup",
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
                ("dose_group_id", models.IntegerField()),
                (
                    "n",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "incidence",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
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
                    "significant",
                    models.BooleanField(
                        default=False,
                        verbose_name=b"Statistically significant from control",
                    ),
                ),
                (
                    "significance_level",
                    models.FloatField(
                        default=None,
                        null=True,
                        verbose_name=b"Statistical significance level",
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(1),
                        ],
                    ),
                ),
                (
                    "endpoint",
                    models.ForeignKey(
                        related_name="endpoint_group",
                        to="animal.Endpoint",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ("endpoint", "dose_group_id")},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Experiment",
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
                        help_text=b"Short-text used to describe the experiment (i.e. 2-year cancer bioassay, 28-day inhalation, etc.).",
                        max_length=80,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        help_text=b"Type of study being performed; be as specific as-possible",
                        max_length=2,
                        choices=[
                            (b"Ac", b"Acute (<24 hr)"),
                            (b"St", b"Short-term (1-30 days)"),
                            (b"Sb", b"Subchronic (30-90 days)"),
                            (b"Ch", b"Chronic (>90 days)"),
                            (b"Ca", b"Cancer"),
                            (b"Me", b"Mechanistic"),
                            (b"Rp", b"Reproductive"),
                            (b"Dv", b"Developmental"),
                            (b"Ot", b"Other"),
                            (b"NR", b"Not-reported"),
                        ],
                    ),
                ),
                (
                    "chemical",
                    models.CharField(max_length=128, verbose_name=b"Chemical name", blank=True),
                ),
                (
                    "cas",
                    models.CharField(
                        help_text=b"CAS number for chemical-tested, if available.",
                        max_length=40,
                        verbose_name=b"Chemical identifier (CAS)",
                        blank=True,
                    ),
                ),
                (
                    "chemical_source",
                    models.CharField(
                        max_length=128, verbose_name=b"Source of chemical", blank=True
                    ),
                ),
                (
                    "purity_available",
                    models.BooleanField(default=True, verbose_name=b"Chemical purity available?"),
                ),
                (
                    "purity",
                    models.FloatField(
                        blank=True,
                        help_text=b"Assumed to be greater-than numeric-value specified (ex: > 95.5%)",
                        null=True,
                        verbose_name=b"Chemical purity (%)",
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "vehicle",
                    models.CharField(
                        help_text=b"If a vehicle was used, vehicle common-name",
                        max_length=64,
                        verbose_name=b"Chemical vehicle",
                        blank=True,
                    ),
                ),
                (
                    "diet",
                    models.TextField(
                        help_text=b"Description of animal-feed, if relevant", blank=True
                    ),
                ),
                (
                    "guideline_compliance",
                    models.CharField(
                        help_text=b"Description of any compliance methods used (i.e. use of EPA\n            OECD, NTP, or other guidelines; conducted under GLP guideline\n            conditions, non-GLP but consistent with guideline study, etc.)",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "litter_effects",
                    models.CharField(
                        default=b"NA",
                        help_text=b"Type of controls used for litter-effects",
                        max_length=2,
                        choices=[
                            (b"NA", b"Not-applicable"),
                            (b"NR", b"Not-reported"),
                            (b"YS", b"Yes, statistical controls"),
                            (b"YD", b"Yes, study-design"),
                            (b"N", b"No"),
                            (b"O", b"Other"),
                        ],
                    ),
                ),
                (
                    "litter_effect_notes",
                    models.CharField(
                        help_text=b"Any additional notes describing how litter effects were controlled",
                        max_length=128,
                        blank=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text=b"Text-description of the experimental protocol used. May also include information such as animal husbandry. Note that dosing-regime information and animal details are captured in other fields.",
                        verbose_name=b"Description and animal husbandry",
                        blank=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "study",
                    models.ForeignKey(
                        related_name="experiments", to="study.Study", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="IndividualAnimal",
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
                ("response", models.FloatField()),
                (
                    "endpoint_group",
                    models.ForeignKey(
                        related_name="individual_data",
                        to="animal.EndpointGroup",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ReferenceValue",
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
                    "point_of_departure",
                    models.FloatField(validators=[django.core.validators.MinValueValidator(0)]),
                ),
                (
                    "type",
                    models.PositiveSmallIntegerField(
                        default=1,
                        choices=[
                            (1, b"Oral RfD"),
                            (2, b"Inhalation RfD"),
                            (3, b"Oral CSF"),
                            (4, b"Inhalation CSF"),
                        ],
                    ),
                ),
                ("justification", models.TextField()),
                ("aggregate_uf", models.FloatField(blank=True)),
                ("reference_value", models.FloatField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "aggregation",
                    models.ForeignKey(
                        help_text=b"Specify a collection of endpoints which justify this reference-value",
                        to="animal.Aggregation",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "assessment",
                    models.ForeignKey(
                        related_name="reference_values",
                        to="assessment.Assessment",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "units",
                    models.ForeignKey(
                        related_name="units+", to="animal.DoseUnits", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Species",
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
                        help_text=b"Enter species in singular (ex: Mouse, not Mice)",
                        unique=True,
                        max_length=30,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("name",), "verbose_name_plural": "species"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Strain",
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
                ("name", models.CharField(max_length=30)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("species", models.ForeignKey(to="animal.Species", on_delete=models.CASCADE)),
            ],
            options={"ordering": ("species", "name")},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UncertaintyFactorEndpoint",
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
                    "uf_type",
                    models.CharField(
                        max_length=3,
                        verbose_name=b"Uncertainty Value Type",
                        choices=[
                            (b"UFA", b"Interspecies uncertainty"),
                            (b"UFH", b"Intraspecies variability"),
                            (b"UFS", b"Subchronic to chronic extrapolation"),
                            (b"UFL", b"Use of a LOAEL in absence of a NOAEL"),
                            (b"UFD", b"Database incomplete"),
                            (b"UFO", b"Other"),
                        ],
                    ),
                ),
                (
                    "value",
                    models.FloatField(
                        default=10.0,
                        help_text=b"Note that 3*3=10 for all uncertainty value calculations; therefore specifying 3.33 is not required.",
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "description",
                    models.TextField(verbose_name=b"Justification", blank=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "endpoint",
                    models.ForeignKey(
                        related_name="ufs", to="animal.Endpoint", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="UncertaintyFactorRefVal",
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
                    "uf_type",
                    models.CharField(
                        max_length=3,
                        verbose_name=b"Uncertainty Value Type",
                        choices=[
                            (b"UFA", b"Interspecies uncertainty"),
                            (b"UFH", b"Intraspecies variability"),
                            (b"UFS", b"Subchronic to chronic extrapolation"),
                            (b"UFL", b"Use of a LOAEL in absence of a NOAEL"),
                            (b"UFD", b"Database incomplete"),
                            (b"UFO", b"Other"),
                        ],
                    ),
                ),
                (
                    "value",
                    models.FloatField(
                        default=10.0,
                        help_text=b"Note that 3*3=10 for all uncertainty value calculations; therefore specifying 3.33 is not required.",
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "description",
                    models.TextField(verbose_name=b"Justification", blank=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "reference_value",
                    models.ForeignKey(
                        related_name="ufs", to="animal.ReferenceValue", on_delete=models.CASCADE
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="uncertaintyfactorrefval",
            unique_together=set([("reference_value", "uf_type")]),
        ),
        migrations.AlterUniqueTogether(
            name="uncertaintyfactorendpoint",
            unique_together=set([("endpoint", "uf_type")]),
        ),
        migrations.AlterUniqueTogether(
            name="strain",
            unique_together=set([("species", "name")]),
        ),
        migrations.AlterUniqueTogether(
            name="referencevalue",
            unique_together=set([("assessment", "type", "units")]),
        ),
        migrations.AddField(
            model_name="dosegroup",
            name="dose_regime",
            field=models.ForeignKey(
                related_name="doses", to="animal.DosingRegime", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="dosegroup",
            name="dose_units",
            field=models.ForeignKey(to="animal.DoseUnits", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="animalgroup",
            name="dosing_regime",
            field=models.ForeignKey(
                blank=True,
                to="animal.DosingRegime",
                on_delete=models.SET_NULL,
                help_text=b"Specify an existing dosing regime or create a new dosing regime below",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="animalgroup",
            name="experiment",
            field=models.ForeignKey(
                related_name="animal_groups", on_delete=models.CASCADE, to="animal.Experiment"
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="animalgroup",
            name="parents",
            field=models.ManyToManyField(
                related_name="children", null=True, to="animal.AnimalGroup", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="animalgroup",
            name="siblings",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="animal.AnimalGroup",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="animalgroup",
            name="species",
            field=models.ForeignKey(to="animal.Species", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="animalgroup",
            name="strain",
            field=models.ForeignKey(to="animal.Strain", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="aggregation",
            name="dose_units",
            field=models.ForeignKey(to="animal.DoseUnits", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="aggregation",
            name="endpoints",
            field=models.ManyToManyField(
                help_text=b"All endpoints entered for assessment.",
                related_name="aggregation",
                to="animal.Endpoint",
            ),
            preserve_default=True,
        ),
    ]
