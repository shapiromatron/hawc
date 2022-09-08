# Generated by Django 3.2.15 on 2022-09-08 17:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("epi", "0018_django31"),
        ("study", "0012_study_eco"),
    ]

    operations = [
        migrations.CreateModel(
            name="NestedTerm",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("path", models.CharField(max_length=255, unique=True)),
                ("depth", models.PositiveIntegerField()),
                ("numchild", models.PositiveIntegerField(default=0)),
                ("name", models.CharField(max_length=128)),
                (
                    "type",
                    models.CharField(choices=[("CE", "cause/effect")], default="CE", max_length=2),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("notes", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
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
                ("value", models.CharField(max_length=128)),
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
            name="Effect",
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
                        blank=True,
                        help_text="Name to refer to this effect/response, commonly used in visualizations",
                        max_length=128,
                    ),
                ),
                (
                    "species",
                    models.CharField(
                        blank=True,
                        help_text="Species name, if applicable; using Common name (Latin binomial)",
                        max_length=128,
                        verbose_name="Species",
                    ),
                ),
                (
                    "units",
                    models.CharField(
                        help_text="Units associated with the effect/response, if applicable",
                        max_length=128,
                        verbose_name="Units",
                    ),
                ),
                (
                    "as_reported",
                    models.TextField(
                        blank=True,
                        help_text="Copy and paste exact phrase up to 1-2 sentences from article. This may be useful for future machine-learning applications.",
                        verbose_name="Effect (as reported)",
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        blank=True,
                        help_text="Additional information not previously described",
                        verbose_name="Comments",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "biological_organization",
                    models.ForeignKey(
                        blank=True,
                        help_text="Level of biological organization associated with the effect/response, if applicable",
                        limit_choices_to={"category": 5},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Level of biological organization",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="eco_effects",
                        to="study.study",
                    ),
                ),
                (
                    "term",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="effects",
                        to="eco.nestedterm",
                    ),
                ),
            ],
            options={
                "verbose_name": "Effect/Response",
            },
        ),
        migrations.CreateModel(
            name="Design",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=128)),
                (
                    "habitat_as_reported",
                    models.TextField(
                        blank=True,
                        help_text="Copy and paste exact phrase up to 1-2 sentences from article. If not stated in the article, leave blank.",
                        verbose_name="Habitat as reported",
                    ),
                ),
                (
                    "climate_as_reported",
                    models.TextField(
                        blank=True,
                        help_text="Copy and paste exact phrase up to 1-2 sentences from article. If not stated in the article, leave blank.",
                        verbose_name="Climate as reported",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "climates",
                    models.ManyToManyField(
                        help_text="Select one or more climates to which the evidence applies",
                        limit_choices_to={"category": 11},
                        related_name="_eco_design_climates_+",
                        to="eco.Vocab",
                    ),
                ),
                (
                    "countries",
                    models.ManyToManyField(
                        help_text="Select one or more countries",
                        related_name="eco_designs",
                        to="epi.Country",
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
                    "ecoregions",
                    models.ManyToManyField(
                        help_text="Select one or more Level III Ecoregions, if known",
                        limit_choices_to={"category": 12},
                        related_name="_eco_design_ecoregions_+",
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
                    "states",
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
                        related_name="eco_designs",
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
                "verbose_name": "Ecological Design",
                "verbose_name_plural": "Ecological Designs",
            },
        ),
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
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="Name to refer to this cause, commonly used in visualizations",
                        max_length=128,
                    ),
                ),
                (
                    "species",
                    models.CharField(
                        blank=True,
                        help_text="Species name, if applicable; using Common name (Latin binomial)",
                        max_length=128,
                        verbose_name="Species",
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        help_text="Specific treatment/exposure/dose level or range of levels of the cause measure",
                        max_length=128,
                        verbose_name="Level",
                    ),
                ),
                (
                    "level_value",
                    models.FloatField(
                        blank=True,
                        help_text="Numerical treatment/exposure/dose level, if applicable",
                        null=True,
                        verbose_name="Level (numeric)",
                    ),
                ),
                (
                    "level_units",
                    models.CharField(
                        help_text="Units associated with the cause, if applicable",
                        max_length=128,
                        verbose_name="Value units",
                    ),
                ),
                (
                    "duration",
                    models.CharField(
                        help_text="Duration or range of durations of the treatment/exposure",
                        max_length=128,
                        verbose_name="Duration",
                    ),
                ),
                (
                    "duration_value",
                    models.FloatField(
                        blank=True,
                        help_text="Numeric value of duration of the treatment/exposure",
                        null=True,
                        verbose_name="Duration (numeric)",
                    ),
                ),
                (
                    "duration_units",
                    models.CharField(
                        blank=True,
                        help_text="Units associated with the duration, if applicable",
                        max_length=128,
                        verbose_name="Duration units",
                    ),
                ),
                (
                    "as_reported",
                    models.TextField(
                        blank=True,
                        help_text="Copy and paste exact phrase up to 1-2 sentences from article. This may be useful for future machine-learning applications.",
                        verbose_name="Cause (as reported)",
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        blank=True,
                        help_text="Additional information not previously described",
                        verbose_name="Comments",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "biological_organization",
                    models.ForeignKey(
                        blank=True,
                        help_text="Level of biological organization associated with the cause, if applicable",
                        limit_choices_to={"category": 5},
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eco.vocab",
                        verbose_name="Biological organization",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="eco_causes",
                        to="study.study",
                    ),
                ),
                (
                    "term",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="causes",
                        to="eco.nestedterm",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cause",
            },
        ),
        migrations.CreateModel(
            name="Result",
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
                        help_text="Sort order of multiple responses in visualizations and data tables",
                        verbose_name="Sort order",
                    ),
                ),
                (
                    "relationship_direction",
                    models.IntegerField(
                        choices=[
                            (0, "Increase"),
                            (1, "Decrease"),
                            (2, "Change"),
                            (3, "No change"),
                            (10, "Other"),
                        ],
                        help_text="Direction of cause and effect relationship",
                        verbose_name="Direction of relationship",
                    ),
                ),
                (
                    "relationship_comment",
                    models.TextField(
                        blank=True,
                        help_text="Describe the relationship in 1-2 sentences",
                        verbose_name="Relationship comment",
                    ),
                ),
                (
                    "measure_value",
                    models.FloatField(
                        blank=True,
                        help_text="Numerical response as reported",
                        null=True,
                        verbose_name="Response measure",
                    ),
                ),
                (
                    "derived_value",
                    models.FloatField(
                        blank=True,
                        help_text="Calculated from 'response measure' based on a formula in 'response measure type', if applicable",
                        null=True,
                        verbose_name="Derived response measure",
                    ),
                ),
                (
                    "sample_size",
                    models.IntegerField(
                        blank=True,
                        help_text="Number of samples, if known",
                        null=True,
                        verbose_name="Sample size",
                    ),
                ),
                (
                    "low_variability",
                    models.FloatField(
                        blank=True,
                        help_text="Lower numerical bound of the response variability",
                        null=True,
                        verbose_name="Lower response measure",
                    ),
                ),
                (
                    "upper_variability",
                    models.FloatField(
                        blank=True,
                        help_text="Upper numerical bound of the response variability",
                        null=True,
                        verbose_name="Upper response measure",
                    ),
                ),
                (
                    "modifying_factors",
                    models.CharField(
                        default="",
                        help_text="A comma-separated list of modifying factors, confounding variables, model co-variates, etc. that were analyzed and tested for the potential to influence the relationship between cause and effect",
                        max_length=256,
                        verbose_name="Modifying factors",
                    ),
                ),
                (
                    "modifying_factors_comment",
                    models.TextField(
                        blank=True,
                        help_text="Describe how the important modifying factor(s) affect the relationship in 1-2 sentences. Consider factors associated with the study that have an important influence on the relationship between cause and effect. For example, statistical significance of a co-variate in a model can indicate importance.",
                        max_length=256,
                        verbose_name="Modifying factors comment",
                    ),
                ),
                (
                    "statistical_sig_value",
                    models.FloatField(
                        blank=True,
                        help_text="Numerical value of the statistical significance",
                        null=True,
                        verbose_name="Statistical significance measure value",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Additional information not previously described",
                        verbose_name="Description",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "cause",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="eco.cause"),
                ),
                (
                    "design",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="results",
                        to="eco.design",
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
                        help_text="Response measure type",
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
                        help_text="Statistical significance measure reported",
                        limit_choices_to={"category": 10},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Statistical significance",
                    ),
                ),
                (
                    "variability",
                    models.ForeignKey(
                        help_text="Variability measurement, if applicable",
                        limit_choices_to={"category": 9},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eco.vocab",
                        verbose_name="Response variability",
                    ),
                ),
            ],
            options={
                "verbose_name": "Result",
                "verbose_name_plural": "Results",
                "ordering": ("effect", "sort_order"),
                "unique_together": {("effect", "sort_order")},
            },
        ),
    ]
