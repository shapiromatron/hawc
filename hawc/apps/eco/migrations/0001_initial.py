import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("study", "0011_auto_20190416_2035"),
        ("epi", "0018_django31"),
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
                        help_text="Type the unit associated with the cause term",
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
            ],
            options={"verbose_name": "Cause/Treatment",},
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
                        blank=True, max_length=100, verbose_name="Effect measure detail"
                    ),
                ),
                (
                    "units",
                    models.CharField(
                        help_text="Type the unit associated with the effect term",
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
                        help_text="Comma-separated list of one or more factors that affect the relationship between the cause and effect",
                        max_length=256,
                        verbose_name="Modifying factors",
                    ),
                ),
            ],
            options={"verbose_name": "Effect/Response",},
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
            options={"verbose_name": "Vocabulary", "verbose_name_plural": "Vocabulary",},
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
                    "cause_level",
                    models.CharField(
                        blank=True,
                        help_text="Type the specific treatment/exposure/dose level of the cause measure",
                        max_length=100,
                        verbose_name="Cause treatment level",
                    ),
                ),
                (
                    "cause_level_value",
                    models.FloatField(
                        blank=True,
                        help_text="Type the numeric value of the specific treatment/exposure/dose level of the cause measure",
                        null=True,
                        verbose_name="Cause treatment level value",
                    ),
                ),
                (
                    "cause_level_units",
                    models.CharField(
                        blank=True,
                        help_text="Enter the units of the specific treatment/exposure/dose level of the cause measure",
                        max_length=100,
                        verbose_name="Cause treatment level units",
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
                        help_text="Type the numerical value of the response measure",
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
                (
                    "effect",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="eco.effect"),
                ),
                (
                    "measure_type",
                    models.ForeignKey(
                        blank=True,
                        help_text="Select one response measure type",
                        limit_choices_to=models.Q(("category", 8), ("parent__isnull", False)),
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Response measure type",
                    ),
                ),
                (
                    "statistical_sig_type",
                    models.ForeignKey(
                        blank=True,
                        help_text="Select the type of statistical significance measure reported",
                        limit_choices_to={"category": 10},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Statistical significance measure type",
                    ),
                ),
                (
                    "variability",
                    models.ForeignKey(
                        blank=True,
                        help_text="Select how variability in the response measure was reported, if applicable",
                        limit_choices_to={"category": 9},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Response variability",
                    ),
                ),
            ],
            options={
                "verbose_name": "Quantitative response information",
                "verbose_name_plural": "Quantitative response information",
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
                        blank=True,
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
                (
                    "study_type",
                    models.ForeignKey(
                        help_text="Select the type of study",
                        limit_choices_to={"category": 0},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                    ),
                ),
            ],
            options={"verbose_name": "Metadata", "verbose_name_plural": "Metadata",},
        ),
        migrations.AddField(
            model_name="effect",
            name="bio_org",
            field=models.ForeignKey(
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
        migrations.AddField(
            model_name="effect",
            name="cause",
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="eco.cause"),
        ),
        migrations.AddField(
            model_name="effect",
            name="measure",
            field=models.ForeignKey(
                limit_choices_to={"category": 7},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="eco.vocab",
                verbose_name="Effect measure",
            ),
        ),
        migrations.AddField(
            model_name="effect",
            name="term",
            field=models.ForeignKey(
                limit_choices_to={"category": 6},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="eco.vocab",
                verbose_name="Effect term",
            ),
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
                limit_choices_to={"category": 3},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="eco.vocab",
            ),
        ),
    ]
