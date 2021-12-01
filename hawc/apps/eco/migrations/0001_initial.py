import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("epi", "0018_django31"),
        ("study", "0011_auto_20190416_2035"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cause",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "measure_detail",
                    models.TextField(blank=True, verbose_name="Cause measure detail"),
                ),
                (
                    "units",
                    models.CharField(
                        help_text="Type the unit associated with the cause term. autocomplete?",
                        max_length=100,
                        verbose_name="Cause units",
                    ),
                ),
                (
                    "species",
                    models.CharField(
                        blank=True,
                        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
                        max_length=100,
                        verbose_name="Cause species",
                    ),
                ),
                (
                    "trajectory",
                    models.IntegerField(
                        choices=[
                            (0, "Increase"),
                            (1, "Decrease"),
                            (2, "Change"),
                            (3, "No change"),
                            (10, "Other"),
                        ],
                        help_text="Select qualitative description of how the cause measure changes, if applicable",
                        verbose_name="Cause trajectory",
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True,
                        help_text="Type any other useful information not captured in other fields",
                        verbose_name="Cause comment",
                    ),
                ),
                (
                    "as_reported",
                    models.TextField(
                        help_text="Copy and paste 1-2 sentences from article",
                        verbose_name="Cause as reported",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Cause/Treatment"},
        ),
        migrations.CreateModel(
            name="State",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("code", models.CharField(max_length=2, unique=True)),
                ("name", models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Vocab",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "category",
                    models.IntegerField(
                        choices=[
                            (0, "Study type"),
                            (1, "Study setting"),
                            (2, "Habitat"),
                            (3, "Cause term"),
                            (4, "Cause measure"),
                            (5, "Biological organization"),
                            (6, "Effect term"),
                            (7, "Effect measure"),
                            (8, "Response measure type"),
                            (9, "Response variability"),
                            (10, "Statistical significance measure"),
                            (11, "Climate"),
                            (12, "Ecoregion"),
                        ]
                    ),
                ),
                ("value", models.CharField(max_length=100)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        related_query_name="children",
                        to="eco.vocab",
                    ),
                ),
            ],
            options={
                "verbose_name": "Controlled vocabulary",
                "verbose_name_plural": "Vocabularies",
            },
        ),
        migrations.CreateModel(
            name="Metadata",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "habitat_as_reported",
                    models.TextField(
                        blank=True,
                        help_text="Copy and paste 1-2 sentences from article",
                        verbose_name="Habitat as reported",
                    ),
                ),
                (
                    "climate_as_reported",
                    models.TextField(
                        blank=True,
                        help_text="Copy and paste from article",
                        verbose_name="Climate as reported",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "climate",
                    models.ManyToManyField(
                        help_text="Select one or more climates to which the evidence applies",
                        limit_choices_to={"category": 11},
                        related_name="_eco_metadata_climate_+",
                        to="eco.Vocab",
                    ),
                ),
                (
                    "country",
                    models.ManyToManyField(
                        help_text="Select one or more countries", to="epi.Country"
                    ),
                ),
                (
                    "design",
                    models.ForeignKey(
                        help_text="Select study design",
                        limit_choices_to={"category": 0},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                    ),
                ),
                (
                    "ecoregion",
                    models.ManyToManyField(
                        help_text="Select one or more Level III Ecoregions, if known",
                        limit_choices_to={"category": 12},
                        related_name="_eco_metadata_ecoregion_+",
                        to="eco.Vocab",
                    ),
                ),
                (
                    "habitat",
                    models.ForeignKey(
                        help_text="Select the habitat to which the evidence applies",
                        limit_choices_to={"category": 2},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Habitat",
                    ),
                ),
                (
                    "state",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Select one or more states, if applicable.",
                        to="eco.State",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="eco_metadata",
                        to="study.study",
                    ),
                ),
                (
                    "study_setting",
                    models.ForeignKey(
                        help_text="Select the setting in which evidence was generated",
                        limit_choices_to={"category": 1},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ecological metadata",
                "verbose_name_plural": "Ecological metadata",
            },
        ),
        migrations.CreateModel(
            name="Effect",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "measure_detail",
                    models.CharField(
                        blank=True,
                        help_text="Add help-text. autocomplete?",
                        max_length=100,
                        verbose_name="Effect measure detail",
                    ),
                ),
                (
                    "units",
                    models.CharField(
                        help_text="Type the unit associated with the effect term. autocomplete?",
                        max_length=100,
                        verbose_name="Effect units",
                    ),
                ),
                (
                    "species",
                    models.CharField(
                        blank=True,
                        help_text="Type the species name, if applicable; use the format Common name (Latin binomial)",
                        max_length=100,
                        verbose_name="Effect species",
                    ),
                ),
                (
                    "trajectory",
                    models.IntegerField(
                        choices=[
                            (0, "Increase"),
                            (1, "Decrease"),
                            (2, "Change"),
                            (3, "No change"),
                            (10, "Other"),
                        ],
                        help_text="Select qualitative description of how the effect measure changes in response to the cause trajectory, if applicable",
                        verbose_name="Effect trajectory",
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True,
                        help_text="Type any other useful information not captured in other fields",
                        verbose_name="Effect comment",
                    ),
                ),
                (
                    "as_reported",
                    models.TextField(
                        help_text="Copy and paste 1-2 sentences from article",
                        verbose_name="Effect as reported",
                    ),
                ),
                (
                    "modifying_factors",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated list of one or more factors that affect the relationship between the cause and effect. Autocomplete/tags?",
                        max_length=256,
                        verbose_name="Modifying factors",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "bio_org",
                    models.ForeignKey(
                        blank=True,
                        help_text="Select the level of biological organization associated with the effect, if applicable",
                        limit_choices_to={"category": 5},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Level of biological organization",
                    ),
                ),
                (
                    "cause",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="eco.cause"
                    ),
                ),
                (
                    "measure",
                    models.ForeignKey(
                        help_text="Add help-text. autocomplete?",
                        limit_choices_to={"category": 7},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Effect measure",
                    ),
                ),
                (
                    "term",
                    models.ForeignKey(
                        limit_choices_to={"category": 6},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Effect term",
                    ),
                ),
            ],
            options={"verbose_name": "Effect/Response"},
        ),
        migrations.AddField(
            model_name="cause",
            name="bio_org",
            field=models.ForeignKey(
                blank=True,
                help_text="Select the level of biological organization associated with the cause, if applicable",
                limit_choices_to={"category": 5},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eco.vocab",
                verbose_name="Level of biological organization",
            ),
        ),
        migrations.AddField(
            model_name="cause",
            name="measure",
            field=models.ForeignKey(
                help_text="Add help text - autocomplete field?",
                limit_choices_to={"category": 4},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="eco.vocab",
            ),
        ),
        migrations.AddField(
            model_name="cause",
            name="study",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="study.study"),
        ),
        migrations.AddField(
            model_name="cause",
            name="term",
            field=models.ForeignKey(
                help_text="Add help text - autocomplete field?",
                limit_choices_to={"category": 3},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="eco.vocab",
            ),
        ),
        migrations.CreateModel(
            name="Quantitative",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "sort_order",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Sort order of a multiple responses",
                        verbose_name="Sort order",
                    ),
                ),
                (
                    "cause_level",
                    models.CharField(
                        help_text="Type the specific treatment/exposure/dose level of the cause measure",
                        max_length=128,
                        verbose_name="Treatment level",
                    ),
                ),
                (
                    "cause_level_value",
                    models.FloatField(
                        blank=True,
                        help_text="Type the numeric value of the specific treatment/exposure/dose level of the cause measure",
                        null=True,
                        verbose_name="Treatment value",
                    ),
                ),
                (
                    "cause_level_units",
                    models.CharField(
                        help_text="Enter the units of the specific treatment/exposure/dose level of the cause measure",
                        max_length=100,
                        verbose_name="Treatment units",
                    ),
                ),
                (
                    "sample_size",
                    models.IntegerField(
                        blank=True,
                        help_text="Type the number of samples used to calculate the response measure value, if known",
                        null=True,
                        verbose_name="Sample size",
                    ),
                ),
                (
                    "measure_value",
                    models.FloatField(
                        blank=True,
                        help_text="Numerical value of the response measure",
                        null=True,
                        verbose_name="Response measure value",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Type any other useful information not captured in other fields",
                        verbose_name="Response measure description",
                    ),
                ),
                (
                    "low_variability",
                    models.FloatField(
                        blank=True,
                        help_text="Type the lower numerical bound of the response variability",
                        null=True,
                        verbose_name="Lower response variability measure",
                    ),
                ),
                (
                    "upper_variability",
                    models.FloatField(
                        blank=True,
                        help_text="Type the upper numerical bound of the response variability",
                        null=True,
                        verbose_name="Upper response variability measure",
                    ),
                ),
                (
                    "statistical_sig_value",
                    models.FloatField(
                        blank=True,
                        help_text="Type the numerical value of the statistical significance",
                        null=True,
                        verbose_name="Statistical significance measure value",
                    ),
                ),
                (
                    "derived_value",
                    models.FloatField(
                        blank=True,
                        help_text="Calculation from 'response measure value' based on a formula linked to 'response measure type', if applicable",
                        null=True,
                        verbose_name="Derived response measure value",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "effect",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="eco.effect"),
                ),
                (
                    "measure_type",
                    models.ForeignKey(
                        help_text="Select one response measure type",
                        limit_choices_to=models.Q(("category", 8), ("parent__isnull", False)),
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Response measure type",
                    ),
                ),
                (
                    "statistical_sig_type",
                    models.ForeignKey(
                        help_text="Select the type of statistical significance measure reported",
                        limit_choices_to={"category": 10},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Statistical significance measure type",
                    ),
                ),
                (
                    "variability",
                    models.ForeignKey(
                        help_text="Select how variability in the response measure was reported, if applicable",
                        limit_choices_to={"category": 9},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Response variability",
                    ),
                ),
            ],
            options={
                "verbose_name": "Quantitative response",
                "verbose_name_plural": "Quantitative responses",
                "ordering": ("effect", "sort_order"),
                "unique_together": {("effect", "sort_order")},
            },
        ),
    ]
