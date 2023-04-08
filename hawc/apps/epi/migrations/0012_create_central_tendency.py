# Generated by Django 1.11.15 on 2019-04-01 23:52

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0014_auto_20190401_1852"),
        ("epi", "0011_py3_unicode"),
    ]

    operations = [
        migrations.CreateModel(
            name="CentralTendency",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "estimate",
                    models.FloatField(
                        blank=True,
                        help_text="Use the central tendency estimate most commonly reported in the set of studies (typically mean or median). Ex. 0.78<span class='help-text-notes'>Note: type and units recorded in other fields</span><span class='important-note'>This field is commonly used in HAWC visualizations</span>",
                        null=True,
                    ),
                ),
                (
                    "estimate_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "---"),
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
                (
                    "variance",
                    models.FloatField(blank=True, null=True, verbose_name="Variance"),
                ),
                (
                    "variance_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "---"),
                            (1, "SD"),
                            (2, "SE"),
                            (3, "SEM"),
                            (4, "GSD"),
                            (5, "other"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "lower_ci",
                    models.FloatField(
                        blank=True,
                        help_text="Numerical value",
                        null=True,
                        verbose_name="Lower CI",
                    ),
                ),
                (
                    "upper_ci",
                    models.FloatField(
                        blank=True,
                        help_text="Numerical value",
                        null=True,
                        verbose_name="Upper CI",
                    ),
                ),
                (
                    "lower_range",
                    models.FloatField(
                        blank=True,
                        help_text="Numerical value",
                        null=True,
                        verbose_name="Lower range",
                    ),
                ),
                (
                    "upper_range",
                    models.FloatField(
                        blank=True,
                        help_text="Numerical value",
                        null=True,
                        verbose_name="Upper range",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Provide additional exposure or extraction details if necessary",
                    ),
                ),
            ],
            options={
                "verbose_name": "Central Tendency",
                "verbose_name_plural": "Central Tendencies",
                "ordering": ("estimate_type",),
            },
        ),
        migrations.AddField(
            model_name="result",
            name="metric_units",
            field=models.TextField(
                blank=True,
                help_text="Note Units: Ex. IQR increase, unit (ng/mL) increase, ln-unit (ng/mL) increase",
            ),
        ),
        migrations.AddField(
            model_name="result",
            name="resulttags",
            field=models.ManyToManyField(
                blank=True, to="assessment.EffectTag", verbose_name="Tags"
            ),
        ),
        migrations.AlterField(
            model_name="comparisonset",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Provide additional comparison set or extraction details if necessary",
            ),
        ),
        migrations.AlterField(
            model_name="comparisonset",
            name="exposure",
            field=models.ForeignKey(
                blank=True,
                help_text="Which exposure group is associated with this comparison set?",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="comparison_sets",
                to="epi.Exposure",
            ),
        ),
        migrations.AlterField(
            model_name="comparisonset",
            name="name",
            field=models.CharField(
                help_text="Name the comparison set, following the format <b>Exposure (If log transformed indicate Ln or Logbase) (If continuous, quartiles, tertiles, etc.) (Any other applicable information on analysis) - identifying characteristics of exposed group.</b> Each group is a collection of people, and all groups in this collection are comparable to one another. You may create a comparison set which contains two groups: cases and controls. Alternatively, for cohort-based studies, you may create a comparison set with four different groups, one for each quartile of exposure based on exposure measurements. Ex. PFNA (Ln) (Tertiles) – newborn boys<span class='help-text-notes'>Common identifying characteristics: cases, controls, newborns, boys, girls, men, women, pregnant women</span>",
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="age_of_exposure",
            field=models.CharField(
                blank=True,
                help_text='When exposure measurement sample was taken, treatment given, and/or specific age or range of ages for which survey data apply; quantitative information (mean, median, SE, range) in parentheses where available.  Ex. Pregnancy (mean 31 years; SD 4 years); Newborn; Adulthood<span class=\'help-text-notes\'>Use age categories "Fetal" (in utero), "Newborn" (at birth), "Neonatal" (0-4 weeks), "Infancy" (0-12 months), "Childhood" (0-11 years), "Adolescence" (12-18 years), "Adulthood" (>18 years); may be assessment specific</span><span class=\'help-text-notes\'>Note "Pregnancy" instead of "Adolescence" or "Adulthood" if applicable</span><span class=\'help-text-notes\'>If multiple, separate with semicolons</span><span class=\'help-text-notes\'>Add units for quantitative measurements (days, months, years)</span>',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="analytical_method",
            field=models.TextField(
                help_text='Lab technique and related information (such as system, corporation name and location) used to measure chemical exposure levels. Ex. "Three PFAS (PFOA, PFOS, and PFHxS) were measured in first-trimester plasma using ultra-high-pressure liquid chromatography (ACQUITY UPLC System; Waters Corporation, Milford, Massachusetts) coupled with tandem mass spectrometry, operated in the multiple reaction monitoring mode with an electrospray ion source in negative mode."'
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="duration",
            field=models.CharField(
                blank=True,
                help_text="Note exposure duration<br/>Ex. Acute, Short-term (2 weeks), Chronic, Developmental, Unclear.<span class='help-text-notes'>In many cases (e.g. most cross-sectional studies) exposure duration will be difficult to establish; use “Unclear” if duration cannot be empirically derived from study design</span>",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="exposure_distribution",
            field=models.CharField(
                blank=True,
                help_text="Enter exposure distribution details not noted in fields below. Ex. 25th percentile=1.18; 75th percentile=3.33<span class='help-text-notes'>Typically 25th and 75th percentiles or alternative central tendency estimate</span>",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="measured",
            field=models.CharField(
                blank=True,
                help_text="Chemical measured in study; typically, the same as chemical exposure, but occasionally chemical exposure metabolite or another chemical signal. Use abbreviation. Ex PFNA; MEHP",
                max_length=128,
                verbose_name="What was measured",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="metric",
            field=models.CharField(
                help_text="In what was the chemical measured? Ex. Air; Maternal serum<span class='help-text-notes'>Exposure medium (ex. air, water), tissue or bodily fluid in which biomarker detected (ex. blood, serum, plasma, urine, feces, breast milk, hair, saliva, teeth, finger or toe nails), or occupation from which exposure assumed (cadmium factory worker)</span><span class='important-note'>This field is commonly used in HAWC visualizations</span>",
                max_length=128,
                verbose_name="Measurement metric",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="metric_description",
            field=models.TextField(
                help_text="Briefly describe how chemical levels in measurement metric were assessed. Ex. Single plasma sample collected for each pregnant woman during the first trimester<span class='help-text-notes'>Note key details or if measurement details not provided. May vary by assessment.</span>",
                verbose_name="Measurement description",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="metric_units",
            field=models.ForeignKey(
                help_text="Note chemical measurement units (metric system); if no units given, that is, chemical exposure assumed from occupation or survey data, note appropriate exposure categories. Ex. ng/mL; Y/N; electroplating/welding/other<span class='important-note'>This field is commonly used in HAWC visualizations</span>",
                on_delete=django.db.models.deletion.CASCADE,
                to="assessment.DoseUnits",
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="n",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span><span class='optional'>Number of individuals where exposure was measured</span>",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="name",
            field=models.CharField(
                help_text="Name of chemical exposure; use abbreviation. Ex. PFNA; DEHP",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="exposure",
            name="sampling_period",
            field=models.CharField(
                blank=True,
                help_text="Exposure sampling period<span class='help-text-notes optional'>Optional</span>",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="comments",
            field=models.TextField(
                blank=True,
                help_text="Provide additional group or extraction details if necessary",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="comparative_name",
            field=models.CharField(
                blank=True,
                help_text='Group and value, displayed in plots, for example "1.5-2.5(Q2) vs ≤1.5(Q1)", or if only one group is available, "4.8±0.2 (mean±SEM)". For categorical, eg., referent; Q2 vs. Q1 The referent group against which exposure or "index" groups are compared is typically the group with the lowest or no exposure',
                max_length=64,
                verbose_name="Comparative Name",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="eligible_n",
            field=models.PositiveIntegerField(
                blank=True, help_text="Optional", null=True, verbose_name="Eligible N"
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="ethnicities",
            field=models.ManyToManyField(blank=True, help_text="Optional", to="epi.Ethnicity"),
        ),
        migrations.AlterField(
            model_name="group",
            name="invited_n",
            field=models.PositiveIntegerField(
                blank=True, help_text="Optional", null=True, verbose_name="Invited N"
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="isControl",
            field=models.NullBooleanField(
                choices=[(True, "Yes"), (False, "No"), (None, "N/A")],
                default=None,
                help_text="Should this group be interpreted as a null/control group, if applicable",
                verbose_name="Control?",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="name",
            field=models.CharField(
                help_text='First note "Cases" or "Controls" if applicable, then "Continuous" for continuous exposure or the appropriate quartile/tertile/etc. for categorial ("Q1", "Q2", etc). Ex. Cases Q3; Continuous',
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="numeric",
            field=models.FloatField(
                blank=True,
                help_text="For categorical, note position in which groups should be listed in visualizations. Ex. Q1: 1 This field is commonly used in HAWC visualizations",
                null=True,
                verbose_name="Numerical value (sorting)",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="participant_n",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Ex. 1400",
                null=True,
                verbose_name="Participant N",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="estimate",
            field=models.FloatField(
                blank=True,
                help_text="Central tendency estimate for group.This field is commonly used in HAWC visualizations",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="is_main_finding",
            field=models.BooleanField(
                default=False,
                help_text='If study does not report a statistically significant association (p<0.05) between exposure and health outcome at any exposure level, check "Main finding" for highest exposure group compared with referent group (e.g.Q4 vs. Q1). If study reports a statistically significant association and monotonic dose response, check "Main finding" for lowest exposure group with a statistically significant association. If nonmonotonic dose response, case-by-case considering statistical trend analyses, consistency of pattern across exposure groups, and/or biological significance.  See "Results" section of https://ehp.niehs.nih.gov/1205502/ for examples and further details. This field is commonly used in HAWC visualizations',
                verbose_name="Main finding",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="lower_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for lower-confidence interval, when available.This field is commonly used in HAWC visualizations",
                null=True,
                verbose_name="Lower CI",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="lower_range",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for lower range, when available.This field is commonly used in HAWC visualizations",
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
                help_text='Select appropriate level of support for the main finding.See "Results" section of https://ehp.niehs.nih.gov/1205502/ for examples and further details. Choose between "inconclusive" vs. "not-supportive" based on chemical- and study-specific context. This field is commonly used in HAWC visualizations',
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="n",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Individuals in group where outcome was measured.This field is commonly used in HAWC visualizations",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="p_value",
            field=models.FloatField(
                blank=True,
                help_text="Note p-value when available. This field is commonly used in HAWC visualizations",
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
                help_text="Select n.s. if results are not statistically significant; otherwise, choose the appropriate qualifier. This field is commonly used in HAWC visualizations",
                max_length=1,
                verbose_name="p-value qualifier",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="upper_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for upper-confidence interval, when available.This field is commonly used in HAWC visualizations",
                null=True,
                verbose_name="Upper CI",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="upper_range",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for upper range, when available.This field is commonly used in HAWC visualizations",
                null=True,
                verbose_name="Upper range",
            ),
        ),
        migrations.AlterField(
            model_name="groupresult",
            name="variance",
            field=models.FloatField(
                blank=True,
                help_text="Variance estimate for group, when available.This field is commonly used in HAWC visualizations",
                null=True,
                verbose_name="Variance",
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="age_of_measurement",
            field=models.CharField(
                blank=True,
                help_text='State study population’s age category at outcome measurement, with quantitative information (mean, median, SE, range) in parentheses where available.<br/>Ex. Pregnancy (mean 31 years;  SD 4 years); Newborn; Adulthood <span class=\'help-text-notes\'>Use age categories "Fetal" (in utero), "Newborn" (at birth), "Neonatal" (0-4 weeks), "Infancy" (0-12 months), "Childhood" (0-11 years), "Adolescence" (12-18 years), "Adulthood" (>18 years); may be assessment specific</span><span class=\'help-text-notes\'>Note "Pregnancy" instead of "Adolescence" or "Adulthood" if applicable</span><span class=\'help-text-notes\'>If multiple, separate with semicolons</span><span class=\'help-text-notes\'>Add units for quantitative measurements (days, months, years)</span>',
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
                    (7, "registry"),
                    (6, "other"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="diagnostic_description",
            field=models.TextField(
                help_text="Copy and paste diagnostic methods directly from study. Ex. \"Birth weight (grams) was measured by trained midwives at delivery.\" <span class='help-text-notes'>Use quotation marks around direct quotes from a study</span>"
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="effect",
            field=models.CharField(
                blank=True,
                help_text="Effect, using common-vocabulary. Use title style (capitalize all words). Ex. Thyroid Hormones",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="effect_subtype",
            field=models.CharField(
                blank=True,
                help_text="Effect subtype, using common-vocabulary. Use title style (capitalize all words). Ex. Absolute<span class='help-text-notes'>This field is not mandatory; often no effect subtype is necessary</span>",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="outcome_n",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Number of individuals for whom outcome was reported. Ex. 132",
                null=True,
                verbose_name="Outcome N",
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="summary",
            field=models.TextField(
                blank=True,
                help_text="Provide additional outcome or extraction details if necessary. Ex. No association (data not shown)",
            ),
        ),
        migrations.AlterField(
            model_name="outcome",
            name="system",
            field=models.CharField(
                blank=True,
                help_text="Primary biological system affected",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="ci_units",
            field=models.FloatField(
                blank=True,
                default=0.95,
                help_text="Write as a decimal: a 95% CI should be recorded as 0.95. Ex. 0.95",
                null=True,
                verbose_name="Confidence interval (CI)",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="comments",
            field=models.TextField(
                blank=True,
                help_text="Summarize main findings (optional) or describe why no details are presented. Ex. No association (data not shown)",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="data_location",
            field=models.CharField(
                blank=True,
                help_text="Details on where the data are found in the literature. Ex. Figure 1; Supplemental Table 2",
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
                help_text="<span class='help-text-notes optional'>Optional</span>",
                verbose_name="Dose Response Trend",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="dose_response_details",
            field=models.TextField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span>",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="metric",
            field=models.ForeignKey(
                help_text="Select the most specific term for the result metric",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="results",
                to="epi.ResultMetric",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="metric_description",
            field=models.TextField(
                blank=True,
                help_text='Specify metric if "other"; optionally, provide details. Ex. Bayesian hierarchical linear regression estimates (betas) and 95% CI between quartile increases in maternal plasma PFAS concentrations (ug/L) and ponderal index (kg/m^3)',
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="name",
            field=models.CharField(
                help_text="Name the result, following the format <b>Effect Exposure (If log-transformed) (continuous, quartiles, tertiles, etc.) – subgroup</b>. Ex. Hyperthyroidism PFHxS (ln) (continuous) – women<span class='important-note'>This field is commonly used in HAWC visualizations</span>",
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="population_description",
            field=models.CharField(
                blank=True,
                help_text="Describe the population subset studied for this outcome, following the format <b>Male or female adults or children (n)</b>. Ex. Women (n=1200); Newborn girls (n=33)<span class='important-note'>This field is commonly used in HAWC visualizations</span>",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="prevalence_incidence",
            field=models.CharField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span>",
                max_length=128,
                verbose_name="Overall incidence prevalence",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="statistical_power",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not reported or calculated"),
                    (1, "appears to be adequately powered (sample size met)"),
                    (
                        2,
                        "somewhat underpowered (sample size is 75% to <100% of recommended)",
                    ),
                    (3, "underpowered (sample size is 50 to <75% required)"),
                    (4, "severely underpowered (sample size is <50% required)"),
                ],
                default=0,
                help_text="Is the study sufficiently powered?<span class='help-text-notes optional'>Optional</span>",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="statistical_power_details",
            field=models.TextField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span>",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="statistical_test_results",
            field=models.TextField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span>",
            ),
        ),
        migrations.AlterField(
            model_name="result",
            name="trend_test",
            field=models.CharField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span><span class='optional'>Enter result, if available (ex: p=0.015, p≤0.05, n.s., etc.)</span>",
                max_length=128,
                verbose_name="Trend test result",
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="age_profile",
            field=models.CharField(
                blank=True,
                help_text='State study population’s age category, with quantitative information (mean, median, SE, range) in parentheses where available. Ex. Pregnancy (mean 31 years; SD 4 years); Newborn; Adulthood <span class=\'help-text-notes\'>Use age categories "Fetal" (in utero), "Newborn" (at birth), "Neonatal" (0-4 weeks), "Infancy" (0-12 months), "Childhood" (0-11 years), "Adolescence" (12-18 years), "Adulthood" (>18 years); may be assessment specific.</span><span class=\'help-text-notes\'>Note "Pregnancy" instead of "Adolescence" or "Adulthood" if applicable.</span><span class=\'help-text-notes\'>If multiple, separate with semicolons.</span><span class=\'help-text-notes\'>Add units for quantitative measurements (days, months, years).</span>',
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="comments",
            field=models.TextField(
                blank=True,
                help_text='Copy-paste text describing study population selection <br/>Ex. "Data and biospecimens were obtained from the Maternal Infant Research on Environmental Chemicals (MIREC) Study, a trans-Canada cohort study of 2,001 pregnant women. Study participants were recruited from 10 Canadian cities between 2008 and 2011. Briefly, women were eligible for inclusion if the fetus was at <14 weeks’ gestation at the time of recruitment and they were ≥18 years of age, able to communicate in French or English, and planning on delivering at a local hospital. Women with known fetal or chromosomal anomalies in the current pregnancy and women with a history of medical complications (including renal disease, epilepsy, hepatitis, heart disease, pulmonary disease, cancer, hematological disorders, threatened spontaneous abortion, and illicit drug use) were excluded from the study."',
            ),
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
                    ("EC", "Ecological"),
                    ("OT", "Other"),
                ],
                help_text="Choose the most specific description of study design.<span class='important-note'>This field is commonly used in HAWC visualizations</span>",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="eligible_n",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span><span class='optional'>Number of individuals eligible based on study design and inclusion/exclusion criteria.</span>",
                null=True,
                verbose_name="Eligible N",
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="invited_n",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span><span class='optional'>Number of individuals initially asked to participate in the study.</span>",
                null=True,
                verbose_name="Invited N",
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="name",
            field=models.CharField(
                help_text="Name the population associated with the study, following the format <b>Study name (years study conducted), Country, number participants (number male, number female, if relevant).</b> Ex. INUENDO (2002-2004), Greenland/Poland/Ukraine, 1,321 mother-infant pairs; NHANES (2007-2010), U.S., 1,181 adults (672 men, 509 women). <span class='help-text-notes'>Use men/women for adults (>=18), boys/girls for children (<18).</span><span class='help-text-notes'>Note pregnant women if applicable.</span><span class='help-text-notes'>There may be multiple study populations within a single study, though this is typically unlikely.</span><span class='important-note'>This field is commonly used in HAWC visualizations</span>",
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="participant_n",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="How many individuals participated in the study? Ex. 1321<br/><span class='help-text-notes'>If mother-infant pairs, note number of pairs, not total individuals studied</span>",
                null=True,
                verbose_name="Participant N",
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="region",
            field=models.CharField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span>",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="source",
            field=models.CharField(
                blank=True,
                help_text="Population source (General population, Occupational cohort, Superfund site, etc.). Ex. General population",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="studypopulation",
            name="state",
            field=models.CharField(
                blank=True,
                help_text="<span class='help-text-notes optional'>Optional</span>",
                max_length=128,
            ),
        ),
        migrations.AddField(
            model_name="centraltendency",
            name="exposure",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="central_tendencies",
                to="epi.Exposure",
            ),
        ),
    ]
