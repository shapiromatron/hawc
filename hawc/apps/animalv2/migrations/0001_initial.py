# Generated by Django 5.0.6 on 2024-07-10 22:02

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("assessment", "0048_assessment_animal_version"),
        ("study", "0012_study_eco"),
        ("vocab", "0006_require_uid"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataExtraction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("is_qualitative_only", models.BooleanField(default=False)),
                (
                    "data_location",
                    models.CharField(
                        blank=True,
                        help_text='Details on where the data are found in the literature (ex: "Figure 1", "Table 2", "Text, p. 24", "Figure 1 and Text, p.24")',
                        max_length=128,
                    ),
                ),
                (
                    "dataset_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("C", "Continuous"),
                            ("D", "Dichotomous"),
                            ("PD", "Percent Difference"),
                            ("DC", "Dichotomous Cancer"),
                            ("NR", "Not reported"),
                        ],
                        default="",
                        max_length=2,
                    ),
                ),
                (
                    "variance_type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "NA"), (1, "SD"), (2, "SE"), (3, "NR")], default=1
                    ),
                ),
                (
                    "statistical_method",
                    models.CharField(blank=True, help_text="TODO", max_length=128),
                ),
                (
                    "statistical_power",
                    models.CharField(blank=True, help_text="TODO", max_length=128),
                ),
                (
                    "method_to_control_for_litter_effects",
                    models.PositiveSmallIntegerField(choices=[(0, "Yes"), (1, "NR"), (2, "NA")]),
                ),
                (
                    "values_estimated",
                    models.BooleanField(
                        default=False,
                        help_text="Response values were estimated using a digital ruler or other methods",
                    ),
                ),
                (
                    "response_units",
                    models.CharField(
                        blank=True,
                        help_text="Units the response was measured in (i.e., μg/dL, % control, etc.)",
                        max_length=32,
                    ),
                ),
                ("dose_response_observations", models.TextField(help_text="TODO")),
                ("result_details", models.TextField(help_text="TODO")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="DoseResponseAnimalLevelData",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("cage_id", models.CharField(blank=True, help_text="TODO", max_length=128)),
                ("animal_id", models.CharField(blank=True, help_text="TODO", max_length=128)),
                ("dose", models.CharField(help_text="TODO", max_length=128)),
                ("response", models.FloatField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "data_extraction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_animal_level_data",
                        to="animalv2.dataextraction",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DoseResponseGroupLevelData",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("treatment_name", models.CharField(help_text="TODO", max_length=256)),
                ("dose", models.CharField(help_text="TODO", max_length=128)),
                (
                    "n",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("response", models.FloatField()),
                (
                    "variance",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "treatment_related_effect",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "Yes"), (1, "No"), (2, "NA"), (3, "NR")]
                    ),
                ),
                (
                    "statistically_significant",
                    models.PositiveSmallIntegerField(choices=[(0, "Yes"), (1, "No"), (2, "NA")]),
                ),
                ("p_value", models.CharField(blank=True, help_text="TODO", max_length=128)),
                (
                    "NOEL",
                    models.SmallIntegerField(default=-999, help_text="No observed effect level"),
                ),
                (
                    "LOEL",
                    models.SmallIntegerField(
                        default=-999, help_text="Lowest observed effect level"
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "data_extraction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_group_level_data",
                        to="animalv2.dataextraction",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Endpoint",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, help_text="Endpoint/Adverse Outcome", max_length=128
                    ),
                ),
                (
                    "system",
                    models.CharField(
                        blank=True, help_text="Relevant biological system", max_length=128
                    ),
                ),
                (
                    "organ",
                    models.CharField(
                        blank=True,
                        help_text="Relevant organ or tissue",
                        max_length=128,
                        verbose_name="Organ (and tissue)",
                    ),
                ),
                (
                    "effect",
                    models.CharField(
                        blank=True, help_text="Effect, using common-vocabulary", max_length=128
                    ),
                ),
                (
                    "effect_subtype",
                    models.CharField(
                        blank=True,
                        help_text="Effect subtype, using common-vocabulary",
                        max_length=128,
                    ),
                ),
                ("effect_modifier_timing", models.CharField(blank=True, max_length=128)),
                ("effect_modifier_reference", models.CharField(blank=True, max_length=128)),
                ("effect_modifier_anatomical", models.CharField(blank=True, max_length=128)),
                ("effect_modifier_location", models.CharField(blank=True, max_length=128)),
                ("comments", models.TextField(blank=True, help_text="TODO")),
                ("additional_tags", models.ManyToManyField(blank=True, to="assessment.effecttag")),
                (
                    "effect_subtype_term",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="v2_endpoint_effect_subtype_terms",
                        to="vocab.term",
                    ),
                ),
                (
                    "effect_term",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="v2_endpoint_effect_terms",
                        to="vocab.term",
                    ),
                ),
                (
                    "name_term",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="v2_endpoint_name_terms",
                        to="vocab.term",
                    ),
                ),
                (
                    "organ_term",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="v2_endpoint_organ_terms",
                        to="vocab.term",
                    ),
                ),
                (
                    "system_term",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="v2_endpoint_system_terms",
                        to="vocab.term",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="dataextraction",
            name="endpoint",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="v2_data_extractions",
                to="animalv2.endpoint",
            ),
        ),
        migrations.CreateModel(
            name="Experiment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Short-text used to describe the experiment (i.e. 2-Year Cancer Bioassay, 10-Day Oral, 28-Day Inhalation, etc.) using title style (all words capitalized). If study contains more than one chemical, then also include the chemical name (e.g. 28-Day Oral PFBS).",
                        max_length=80,
                        verbose_name="Experiment name",
                    ),
                ),
                (
                    "design",
                    models.CharField(
                        choices=[("AA", "TODO A"), ("BB", "TODO B")],
                        help_text="Design of study being performed",
                        max_length=2,
                    ),
                ),
                ("has_multiple_generations", models.BooleanField(default=False)),
                (
                    "guideline_compliance",
                    models.CharField(
                        blank=True,
                        help_text='Description of any compliance methods used (i.e. use of EPA OECD, NTP, or other guidelines; conducted under GLP guideline conditions, non-GLP but consistent with guideline study, etc.). This field response should match any description used in study evaluation in the reporting quality domain, e.g., GLP study (OECD guidelines 414 and 412, 1981 versions). If not reported, then use state "not reported."',
                        max_length=128,
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        blank=True,
                        help_text="Additional comments (eg., description, animal husbandry, etc.)",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_experiments",
                        to="study.study",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="endpoint",
            name="experiment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="v2_endpoints",
                to="animalv2.experiment",
            ),
        ),
        migrations.AddField(
            model_name="dataextraction",
            name="experiment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="v2_data_extractions",
                to="animalv2.experiment",
            ),
        ),
        migrations.CreateModel(
            name="Chemical",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="This field may get displayed in visualizations, so consider using a common acronym, e.g., BPA instead of Bisphenol A",
                        max_length=80,
                        verbose_name="Chemical name",
                    ),
                ),
                (
                    "cas",
                    models.CharField(
                        blank=True,
                        help_text="CAS number for chemical-tested. Use N/A if not applicable. If more than one CAS number is applicable, then use a common one here and indicate others in the comment field below.",
                        max_length=40,
                        verbose_name="Chemical identifier (CAS)",
                    ),
                ),
                (
                    "source",
                    models.CharField(blank=True, max_length=128, verbose_name="Source of chemical"),
                ),
                (
                    "purity",
                    models.CharField(blank=True, max_length=128, verbose_name="Chemical purity"),
                ),
                (
                    "vehicle",
                    models.CharField(
                        blank=True,
                        help_text='Describe vehicle (use name as described in methods but also add the common name if the vehicle was described in a non-standard way). Enter "not reported" if the vehicle is not described. For inhalation studies, air can be inferred if not explicitly reported. Examples: "corn oil," "filtered air," "not reported, but assumed clean air."',
                        max_length=64,
                        verbose_name="Chemical vehicle",
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        blank=True,
                        help_text="Additional comments (eg., description, animal husbandry, etc.)",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "dtxsid",
                    models.ForeignKey(
                        blank=True,
                        help_text='<a rel="noopener noreferrer" target="_blank" href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DssTox</a> substance identifier (recommended). When using an identifier, chemical name and CASRN are standardized using the <a href="https://comptox.epa.gov/dashboard/" rel="noopener noreferrer" target="_blank">DTXSID</a>.',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="v2_chemicals",
                        to="assessment.dsstox",
                        verbose_name="DSSTox substance identifier (DTXSID)",
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_chemicals",
                        to="animalv2.experiment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AnimalGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name should be: sex, common strain name, species (plural) and use Title Style (e.g. Male Sprague Dawley Rat, Female C57BL/6 Mice, Male and Female C57BL/6 Mice). For developmental studies, include the generation before sex in title (e.g., F1 Male Sprague Dawley Rat or P0 Female C57 Mice)",
                        max_length=80,
                        verbose_name="Animal group name",
                    ),
                ),
                (
                    "sex",
                    models.CharField(
                        choices=[
                            ("M", "Male"),
                            ("F", "Female"),
                            ("C", "Combined"),
                            ("R", "Not reported"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "animal_source",
                    models.CharField(
                        blank=True,
                        help_text="Source from where animals were acquired",
                        max_length=128,
                    ),
                ),
                (
                    "lifestage_at_exposure",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("DEV", "Developmental"),
                            ("JUV", "Juvenile"),
                            ("ADULT", "Adult"),
                            ("AG", "Adult (gestation)"),
                            ("ML", "Multi-lifestage"),
                        ],
                        default="",
                        help_text="Definitions: <strong>Developmental</strong>: Prenatal and perinatal exposure in dams or postnatal exposure in offspring until sexual maturity (~6 weeks in rats and mice). Include studies with pre-mating exposure <em>if the endpoint focus is developmental</em>. <strong>Juvenile</strong>: Exposure between weaned and sexual maturity. <strong>Adult</strong>: Exposure in sexually mature males or females. <strong>Adult (gestation)</strong>: Exposure in dams during pregnancy. <strong>Multi-lifestage</strong>: includes both developmental and adult (i.e., multi-generational studies, exposure that start before sexual maturity and continue to adulthood)",
                        max_length=5,
                    ),
                ),
                (
                    "lifestage_at_assessment",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("DEV", "Developmental"),
                            ("JUV", "Juvenile"),
                            ("ADULT", "Adult"),
                            ("AG", "Adult (gestation)"),
                            ("ML", "Multi-lifestage"),
                        ],
                        default="",
                        help_text="Definitions: <strong>Developmental</strong>: Prenatal and perinatal exposure in dams or postnatal exposure in offspring until sexual maturity (~6 weeks in rats and mice). Include studies with pre-mating exposure <em>if the endpoint focus is developmental</em>. <strong>Juvenile</strong>: Exposure between weaned and sexual maturity. <strong>Adult</strong>: Exposure in sexually mature males or females. <strong>Adult (gestation)</strong>: Exposure in dams during pregnancy. <strong>Multi-lifestage</strong>: includes both developmental and adult (i.e., multi-generational studies, exposure that start before sexual maturity and continue to adulthood)",
                        max_length=5,
                    ),
                ),
                (
                    "generation",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "N/A (not generational-study)"),
                            ("P0", "Parent-generation (P0)"),
                            ("F1", "First-generation (F1)"),
                            ("F2", "Second-generation (F2)"),
                            ("F3", "Third-generation (F3)"),
                            ("F4", "Fourth-generation (F4)"),
                            ("Ot", "Other"),
                        ],
                        default="",
                        max_length=2,
                    ),
                ),
                (
                    "husbandry_and_diet",
                    models.TextField(
                        blank=True,
                        help_text='Copy paste animal husbandry information from materials and methods, use quotation marks around all text directly copy/pasted from paper. Describe diet as presented in the paper (e.g., "soy-protein free 2020X Teklad," "Atromin 1310", "standard rodent chow").',
                        verbose_name="Animal Husbandry and Diet",
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "parents",
                    models.ManyToManyField(
                        blank=True, related_name="children", to="animalv2.animalgroup"
                    ),
                ),
                (
                    "species",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_animal_groups",
                        to="assessment.species",
                    ),
                ),
                (
                    "strain",
                    models.ForeignKey(
                        help_text='When adding a new strain, put the stock in parenthesis, e.g., "Sprague-Dawley (Harlan)."',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_animal_groups",
                        to="assessment.strain",
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_animal_groups",
                        to="animalv2.experiment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ObservationTime",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "observation_time",
                    models.FloatField(
                        blank=True,
                        help_text="Numeric value of the time an observation was reported; optional, should be recorded if the same effect was measured multiple times.",
                        null=True,
                        verbose_name="Observation timepoint",
                    ),
                ),
                (
                    "observation_time_units",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "not reported"),
                            (1, "seconds"),
                            (2, "minutes"),
                            (3, "hours"),
                            (4, "days"),
                            (5, "weeks"),
                            (6, "months"),
                            (9, "years"),
                            (7, "post-natal day (PND)"),
                            (8, "gestational day (GD)"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "observation_time_text",
                    models.CharField(
                        blank=True,
                        help_text='Text for reported observation time (ex: "60-90 PND")',
                        max_length=64,
                    ),
                ),
                ("comments", models.TextField(blank=True, help_text="TODO")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "endpoint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_timepoints",
                        to="animalv2.endpoint",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="dataextraction",
            name="observation_timepoint",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="v2_data_extractions",
                to="animalv2.observationtime",
            ),
        ),
        migrations.CreateModel(
            name="Treatment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="TODO", max_length=80, verbose_name="Treatment name"
                    ),
                ),
                (
                    "route_of_exposure",
                    models.CharField(
                        choices=[
                            ("OR", "Oral"),
                            ("OC", "Oral capsule"),
                            ("OD", "Oral diet"),
                            ("OG", "Oral gavage"),
                            ("OW", "Oral drinking water"),
                            ("I", "Inhalation"),
                            ("IG", "Inhalation - gas"),
                            ("IR", "Inhalation - particle"),
                            ("IA", "Inhalation - vapor"),
                            ("D", "Dermal"),
                            ("SI", "Subcutaneous injection"),
                            ("IP", "Intraperitoneal injection"),
                            ("IV", "Intravenous injection"),
                            ("IO", "in ovo"),
                            ("P", "Parental"),
                            ("W", "Whole body"),
                            ("M", "Multiple"),
                            ("U", "Unknown"),
                            ("O", "Other"),
                        ],
                        help_text="Primary route of exposure. If multiple primary-exposures, describe in notes-field below",
                        max_length=2,
                    ),
                ),
                (
                    "exposure_duration",
                    models.FloatField(
                        blank=True,
                        help_text="Length of exposure period (fractions allowed), used for sorting in visualizations. For single-dose or multiple-dose/same day gavage studies, 1.",
                        null=True,
                        verbose_name="Exposure duration (days)",
                    ),
                ),
                (
                    "exposure_duration_description",
                    models.CharField(
                        blank=True,
                        help_text='Length of time between start of exposure and outcome assessment, in days when &lt;7 (e.g., 5d), weeks when &ge;7 days to 12 weeks (e.g., 1wk, 12wk), or months when &gt;12 weeks (e.g., 15mon). For repeated measures use descriptions such as "1, 2 and 3 wk".  For inhalations studies, also include hours per day and days per week, e.g., "13wk (6h/d, 7d/wk)." This field is commonly used in visualizations, so use abbreviations (h, d, wk, mon, y) and no spaces between numbers to save space. For reproductive and developmental studies, where possible instead include abbreviated age descriptions such as "GD1-10" or "GD2-PND10". For gavage studies, include the number of doses, e.g. "1wk (1dose/d, 5d/wk)" or "2doses" for a single-day experiment.',
                        max_length=128,
                        verbose_name="Exposure duration (text)",
                    ),
                ),
                (
                    "exposure_outcome_duration",
                    models.FloatField(
                        blank=True,
                        help_text="Optional: Numeric length of time between start of exposure and outcome assessment in days. This field may be used to sort studies which is why days are used as a common metric.",
                        null=True,
                        verbose_name="Exposure-outcome duration (days)",
                    ),
                ),
                ("comments", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "chemical",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_treatments",
                        to="animalv2.chemical",
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_treatments",
                        to="animalv2.experiment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DoseGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("dose_group_id", models.PositiveSmallIntegerField()),
                (
                    "dose",
                    models.FloatField(validators=[django.core.validators.MinValueValidator(0)]),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "dose_units",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_dose_groups",
                        to="assessment.doseunits",
                    ),
                ),
                (
                    "treatment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="v2_dose_groups",
                        to="animalv2.treatment",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="dataextraction",
            name="treatment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="v2_data_extractions",
                to="animalv2.treatment",
            ),
        ),
    ]
