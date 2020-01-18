# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-02 20:00
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("epi", "0010_result_statistical_test_results"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comparisonset",
            name="exposure",
            field=models.ForeignKey(
                blank=True,
                help_text="Exposure-group associated with this group",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comparison_sets",
                to="epi.Exposure",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="age_of_exposure",
            field=models.CharField(
                blank=True,
                help_text='Textual age description for when exposure measurement sample was taken, treatment given, or age for which survey data apply [examples include:  specific age indicated in the study (e.g., "gestational week 20, 3 years of age, 10-12 years of age, previous 12 months") OR standard age categories: "fetal (in utero), neonatal (0-27 days), infancy (1-12 months) toddler (1-2 years), middle childhood (6-11 years, early adolescence (12-18 years),late adolescence (19-21 years), adulthood (>21),older adulthood (varies)" – based on NICHD Integratedpediatric terminology]',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="analytical_method",
            field=models.TextField(
                help_text="Include details on the lab-techniques for exposure measurement in samples."
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="duration",
            field=models.CharField(blank=True, help_text="Exposure duration", max_length=128),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="estimate",
            field=models.FloatField(blank=True, help_text="Central tendency estimate", null=True),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="estimate_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, None),
                    (1, "mean"),
                    (2, "geometric mean"),
                    (3, "median"),
                    (5, "point"),
                    (4, "other"),
                ],
                default=0,
                verbose_name="Central estimate type",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="exposure_distribution",
            field=models.CharField(
                blank=True,
                help_text='May be used to describe the exposure distribution, for example, "2.05 µg/g creatinine (urine), geometric mean; 25th percentile = 1.18, 75th percentile = 3.33"',
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="iv",
            field=models.BooleanField(default=False, verbose_name="Intravenous (IV)"),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="lower_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for lower-confidence interval",
                null=True,
                verbose_name="Lower CI",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="lower_range",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for lower range",
                null=True,
                verbose_name="Lower range",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="measured",
            field=models.CharField(blank=True, max_length=128, verbose_name="What was measured"),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="metric",
            field=models.CharField(max_length=128, verbose_name="Measurement Metric"),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="metric_description",
            field=models.TextField(verbose_name="Measurement Description"),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="n",
            field=models.PositiveIntegerField(
                blank=True, help_text="Individuals where outcome was measured", null=True,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="name",
            field=models.CharField(help_text="Name of exposure and exposure-route", max_length=128),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="sampling_period",
            field=models.CharField(
                blank=True, help_text="Exposure sampling period", max_length=128
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="upper_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for upper-confidence interval",
                null=True,
                verbose_name="Upper CI",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="upper_range",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for upper range",
                null=True,
                verbose_name="Upper range",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="variance",
            field=models.FloatField(
                blank=True, help_text="Variance estimate", null=True, verbose_name="Variance",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="variance_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, None), (1, "SD"), (2, "SE"), (3, "SEM"), (4, "GSD"), (5, "other")],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="comments",
            field=models.TextField(
                blank=True, help_text="Any other comments related to this group"
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="comparative_name",
            field=models.CharField(
                blank=True,
                help_text='Group and value, displayed in plots, for example "1.5-2.5(Q2) vs ≤1.5(Q1)", or if only one group is available, "4.8±0.2 (mean±SEM)"',
                max_length=64,
                verbose_name="Comparative Name",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="eligible_n",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Eligible N"),
        ),
        migrations.AlterField(
            model_name="group",
            name="invited_n",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Invited N"),
        ),
        migrations.AlterField(
            model_name="group",
            name="isControl",
            field=models.NullBooleanField(
                choices=[(True, "Yes"), (False, "No"), (None, "N/A")],
                default=None,
                help_text="Should this group be interpreted as a null/control group",
                verbose_name="Control?",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="numeric",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value, can be used for sorting",
                null=True,
                verbose_name="Numerical value (sorting)",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="participant_n",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Participant N"),
        ),
        migrations.AlterField(
            model_name="group",
            name="sex",
            field=models.CharField(
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
        migrations.AlterField(
            model_name="groupnumericaldescriptions",
            name="description",
            field=models.CharField(
                help_text="Description if numeric ages do not make sense for this study-population (ex: longitudinal studies)",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="groupnumericaldescriptions",
            name="is_calculated",
            field=models.BooleanField(
                default=False, help_text="Was value calculated/estimated from literature?",
            ),
        ),
        migrations.AlterField(
            model_name="groupnumericaldescriptions",
            name="lower_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, None), (1, "lower limit"), (2, "5% CI"), (3, "other")], default=0,
            ),
        ),
        migrations.AlterField(
            model_name="groupnumericaldescriptions",
            name="mean",
            field=models.FloatField(blank=True, null=True, verbose_name="Central estimate"),
        ),
        migrations.AlterField(
            model_name="groupnumericaldescriptions",
            name="mean_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, None),
                    (1, "mean"),
                    (2, "geometric mean"),
                    (3, "median"),
                    (4, "other"),
                ],
                default=0,
                verbose_name="Central estimate type",
            ),
        ),
        migrations.AlterField(
            model_name="groupnumericaldescriptions",
            name="upper_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, None), (1, "upper limit"), (2, "95% CI"), (3, "other")], default=0,
            ),
        ),
        migrations.AlterField(
            model_name="groupnumericaldescriptions",
            name="variance_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, None), (1, "SD"), (2, "SEM"), (3, "GSD"), (4, "other")], default=0,
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="estimate",
            field=models.FloatField(
                blank=True, help_text="Central tendency estimate for group", null=True
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="is_main_finding",
            field=models.BooleanField(
                help_text="Is this the main-finding for this outcome?", verbose_name="Main finding",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="lower_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for lower-confidence interval",
                null=True,
                verbose_name="Lower CI",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="lower_range",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for lower range",
                null=True,
                verbose_name="Lower range",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="main_finding_support",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (3, "not-reported"),
                    (2, "supportive"),
                    (1, "inconclusive"),
                    (0, "not-supportive"),
                ],
                default=1,
                help_text="Are the results supportive of the main-finding?",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="n",
            field=models.PositiveIntegerField(
                blank=True, help_text="Individuals in group where outcome was measured", null=True,
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="p_value",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(1.0),
                ],
                verbose_name="p-value",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="p_value_qualifier",
            field=models.CharField(
                choices=[(" ", "-"), ("-", "n.s."), ("<", "<"), ("=", "="), (">", ">")],
                default="-",
                max_length=1,
                verbose_name="p-value qualifier",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="upper_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for upper-confidence interval",
                null=True,
                verbose_name="Upper CI",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="upper_range",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for upper range",
                null=True,
                verbose_name="Upper range",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="variance",
            field=models.FloatField(
                blank=True,
                help_text="Variance estimate for group",
                null=True,
                verbose_name="Variance",
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="age_of_measurement",
            field=models.CharField(
                blank=True,
                help_text='Textual age description when outcomes were measured [examples include:  specific age indicated in the study (e.g., "3 years of age, 10-12 years of age") OR standard age categories: "infancy (1-12 months), toddler (1-2 years), middle childhood (6-11 years, early adolescence (12-18 years), late adolescence (19-21 years), adulthood (>21), older adulthood (varies)" - based on NICHD Integrated pediatric terminology]',
                max_length=32,
                verbose_name="Age at outcome measurement",
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="diagnostic",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not reported"),
                    (1, "medical professional or test"),
                    (2, "medical records"),
                    (3, "self-reported"),
                    (4, "questionnaire"),
                    (5, "hospital admission"),
                    (6, "other"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="effect",
            field=models.CharField(
                blank=True, help_text="Effect, using common-vocabulary", max_length=128
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="effect_subtype",
            field=models.CharField(
                blank=True, help_text="Effect subtype, using common-vocabulary", max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="outcome_n",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Outcome N"),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="summary",
            field=models.TextField(
                blank=True,
                help_text='Summarize main findings of outcome, or describe why no details are presented (for example, "no association (data not shown)")',
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="system",
            field=models.CharField(
                blank=True, help_text="Relevant biological system", max_length=128
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="ci_units",
            field=models.FloatField(
                blank=True,
                default=0.95,
                help_text="A 95% CI is written as 0.95.",
                null=True,
                verbose_name="Confidence Interval (CI)",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="comments",
            field=models.TextField(
                blank=True,
                help_text='Summarize main findings of outcome, or describe why no details are presented (for example, "no association (data not shown)")',
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="data_location",
            field=models.CharField(
                blank=True,
                help_text="Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="dose_response",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not-applicable"),
                    (1, "monotonic"),
                    (2, "non-monotonic"),
                    (3, "no trend"),
                    (4, "not reported"),
                ],
                default=0,
                help_text="Was a trend observed?",
                verbose_name="Dose Response Trend",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="estimate_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, None),
                    (1, "mean"),
                    (2, "geometric mean"),
                    (3, "median"),
                    (5, "point"),
                    (4, "other"),
                ],
                default=0,
                verbose_name="Central estimate type",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="metric",
            field=models.ForeignKey(
                help_text="&nbsp;",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="results",
                to="epi.ResultMetric",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="metric_description",
            field=models.TextField(
                blank=True, help_text="Add additional text describing the metric used, if needed.",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="population_description",
            field=models.CharField(
                blank=True,
                help_text='Detailed description of the population being studied forthis outcome, which may be a subset of the entirestudy-population. For example, "US (national) NHANES2003-2008, Hispanic children 6-18 years, ♂♀ (n=797)"',
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="prevalence_incidence",
            field=models.CharField(
                blank=True, max_length=128, verbose_name="Overall incidence prevalence"
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="statistical_power",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not reported or calculated"),
                    (1, "appears to be adequately powered (sample size met)"),
                    (2, "somewhat underpowered (sample size is 75% to <100% of recommended)",),
                    (3, "underpowered (sample size is 50 to <75% required)"),
                    (4, "severely underpowered (sample size is <50% required)"),
                ],
                default=0,
                help_text="Is the study sufficiently powered?",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="trend_test",
            field=models.CharField(
                blank=True,
                help_text="Enter result, if available (ex: p=0.015, p≤0.05, n.s., etc.)",
                max_length=128,
                verbose_name="Trend test result",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="variance_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, None), (1, "SD"), (2, "SE"), (3, "SEM"), (4, "GSD"), (5, "other")],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="resultmetric",
            name="isLog",
            field=models.BooleanField(
                default=True,
                help_text="When plotting, use a log base 10 scale",
                verbose_name="Display as log",
            ),
        ),
        migrations.AlterField(
            model_name="resultmetric",
            name="order",
            field=models.PositiveSmallIntegerField(help_text="Order as they appear in option-list"),
        ),
        migrations.AlterField(
            model_name="resultmetric",
            name="reference_value",
            field=models.FloatField(
                blank=True,
                default=1,
                help_text="Null hypothesis value for reference, if applicable",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="resultmetric",
            name="showForestPlot",
            field=models.BooleanField(
                default=True,
                help_text="Does forest-plot representation of result make sense?",
                verbose_name="Show on forest plot",
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="age_profile",
            field=models.CharField(
                blank=True,
                help_text="Age profile of population (ex: adults, children, pregnant women, etc.)",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="comments",
            field=models.TextField(blank=True, help_text="Note matching criteria, etc."),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="design",
            field=models.CharField(
                choices=[
                    ("CO", "Cohort"),
                    ("CX", "Cohort (Retrospective)"),
                    ("CY", "Cohort (Prospective)"),
                    ("CC", "Case-control"),
                    ("NC", "Nested case-control"),
                    ("CR", "Case report"),
                    ("SE", "Case series"),
                    ("RT", "Randomized controlled trial"),
                    ("NT", "Non-randomized controlled trial"),
                    ("CS", "Cross-sectional"),
                ],
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="eligible_n",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Eligible N"),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="invited_n",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Invited N"),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="participant_n",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Participant N"),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="source",
            field=models.CharField(
                blank=True,
                help_text="Population source (ex: general population, environmental exposure, occupational cohort)",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="studypopulationcriteria",
            name="criteria_type",
            field=models.CharField(
                choices=[("I", "Inclusion"), ("E", "Exclusion"), ("C", "Confounding")],
                max_length=1,
            ),
        ),
    ]
