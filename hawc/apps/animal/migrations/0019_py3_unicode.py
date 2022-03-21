# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-02 20:00
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("animal", "0018_auto_20160602_1007"),
    ]

    operations = [
        migrations.AlterField(
            model_name="animalgroup",
            name="animal_source",
            field=models.CharField(
                blank=True,
                help_text="Laboratory and/or breeding details where animals were acquired",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="comments",
            field=models.TextField(
                blank=True,
                help_text="Any addition notes for this animal-group.",
                verbose_name="Description",
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="dosing_regime",
            field=models.ForeignKey(
                blank=True,
                help_text="Specify an existing dosing regime or create a new dosing regime below",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="animal.DosingRegime",
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="duration_observation",
            field=models.FloatField(
                blank=True,
                help_text="Numeric length of observation period, in days (fractions allowed)",
                null=True,
                verbose_name="Observation duration (days)",
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="generation",
            field=models.CharField(
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
        migrations.AlterField(
            model_name="animalgroup",
            name="lifestage_assessed",
            field=models.CharField(
                blank=True,
                help_text='Textual life-stage description when endpoints were measured (examples include: "parental, PND18, juvenile, adult, multiple")',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="lifestage_exposed",
            field=models.CharField(
                blank=True,
                help_text='Textual life-stage description when exposure occurred (examples include: "parental, PND18, juvenile, adult, continuous, multiple")',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="name",
            field=models.CharField(
                help_text="Short description of the animals (i.e. Male Fischer F344 rats, Female C57BL/6 mice)",
                max_length=80,
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="sex",
            field=models.CharField(
                choices=[("M", "Male"), ("F", "Female"), ("C", "Combined"), ("R", "Not reported")],
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Detailed description of dosing methodology (i.e. exposed via inhalation 5 days/week for 6 hours)",
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="duration_exposure",
            field=models.FloatField(
                blank=True,
                help_text="Length of exposure period (fractions allowed), used for sorting in visualizations",
                null=True,
                verbose_name="Exposure duration (days)",
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="duration_exposure_text",
            field=models.CharField(
                blank=True,
                help_text="Text-description of the exposure duration (ex: 21 days, 104 wks, GD0 to PND9, GD0 to weaning)",
                max_length=128,
                verbose_name="Exposure duration (text)",
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="negative_control",
            field=models.CharField(
                choices=[
                    ("NR", "Not-reported"),
                    ("UN", "Untreated"),
                    ("VT", "Vehicle-treated"),
                    ("B", "Untreated + Vehicle-treated"),
                    ("Y", "Yes (untreated and/or vehicle)"),
                    ("N", "No"),
                ],
                default="NR",
                help_text="Description of negative-controls used",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="num_dose_groups",
            field=models.PositiveSmallIntegerField(
                default=4,
                help_text="Number of dose groups, plus control",
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name="Number of Dose Groups",
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="positive_control",
            field=models.NullBooleanField(
                choices=[(True, "Yes"), (False, "No"), (None, "Unknown")],
                default=None,
                help_text="Was a positive control used?",
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="route_of_exposure",
            field=models.CharField(
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
        migrations.AlterField(
            model_name="endpoint",
            name="FEL",
            field=models.SmallIntegerField(
                default=-999, help_text="Frank effect level", verbose_name="FEL"
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="LOEL",
            field=models.SmallIntegerField(
                default=-999,
                help_text="Lowest observed effect level",
                verbose_name="LOEL",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="NOEL",
            field=models.SmallIntegerField(
                default=-999, help_text="No observed effect level", verbose_name="NOEL"
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="additional_fields",
            field=models.TextField(default="{}"),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="confidence_interval",
            field=models.FloatField(
                blank=True,
                help_text="A 95% CI is written as 0.95.",
                null=True,
                verbose_name="Confidence interval (CI)",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="data_extracted",
            field=models.BooleanField(
                default=True,
                help_text="Dose-response data for endpoint are extracted from literature into HAWC",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="data_location",
            field=models.CharField(
                blank=True,
                help_text="Details on where the data are found in the literature (ex: Figure 1, Table 2, etc.)",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="data_reported",
            field=models.BooleanField(
                default=True,
                help_text="Dose-response data for endpoint are available in the literature source",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="data_type",
            field=models.CharField(
                choices=[
                    ("C", "Continuous"),
                    ("D", "Dichotomous"),
                    ("P", "Percent Difference"),
                    ("DC", "Dichotomous Cancer"),
                    ("NR", "Not reported"),
                ],
                default="C",
                max_length=2,
                verbose_name="Dataset type",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="diagnostic",
            field=models.TextField(
                blank=True,
                help_text="Diagnostic or method used to measure endpoint (if relevant)",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="effect",
            field=models.CharField(
                blank=True, help_text="Effect, using common-vocabulary", max_length=128
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="effect_subtype",
            field=models.CharField(
                blank=True,
                help_text="Effect subtype, using common-vocabulary",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="endpoint_notes",
            field=models.TextField(
                blank=True,
                help_text="Any additional notes related to this endpoint/methodology, not including results",
                verbose_name="General notes/methodology",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="expected_adversity_direction",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (3, "increase from reference/control group"),
                    (2, "decrease from reference/control group"),
                    (1, "any change from reference/control group"),
                    (0, "not reported"),
                ],
                default=0,
                help_text="Response direction which would be considered adverse",
                verbose_name="Expected response adversity direction",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="monotonicity",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "N/A, single dose level study"),
                    (1, "N/A, no effects detected"),
                    (2, "yes, visual appearance of monotonicity but no trend"),
                    (3, "yes, monotonic and significant trend"),
                    (4, "yes, visual appearance of non-monotonic but no trend"),
                    (5, "yes, non-monotonic and significant trend"),
                    (6, "no pattern"),
                    (7, "unclear"),
                    (8, "not-reported"),
                ],
                default=8,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="observation_time",
            field=models.FloatField(
                blank=True,
                help_text="Numeric value of the time an observation was reported; optional, should be recorded if the same effect was measured multiple times.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="observation_time_text",
            field=models.CharField(
                blank=True,
                help_text='Text for reported observation time (ex: "60-90 PND")',
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="observation_time_units",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not-reported"),
                    (1, "seconds"),
                    (2, "minutes"),
                    (3, "hours"),
                    (4, "days"),
                    (5, "weeks"),
                    (6, "months"),
                    (9, "years"),
                    (7, "PND"),
                    (8, "GD"),
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="organ",
            field=models.CharField(
                blank=True,
                help_text="Relevant organ; also include tissue if relevant",
                max_length=128,
                verbose_name="Organ (and tissue)",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="power_notes",
            field=models.TextField(
                blank=True,
                help_text="Power of study-design to detect change from control",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="response_units",
            field=models.CharField(
                blank=True,
                help_text="Units the response was measured in (i.e., μg/dL, % control, etc.)",
                max_length=32,
                verbose_name="Response units",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="results_notes",
            field=models.TextField(blank=True, help_text="Qualitative description of the results"),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="statistical_test",
            field=models.CharField(
                blank=True,
                help_text="Description of statistical analysis techniques used",
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="system",
            field=models.CharField(
                blank=True, help_text="Relevant biological system", max_length=128
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="trend_result",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "not applicable"),
                    (1, "not significant"),
                    (2, "significant"),
                    (3, "not reported"),
                ],
                default=3,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="trend_value",
            field=models.FloatField(
                blank=True,
                help_text="Numerical result for trend-test, if available",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="values_estimated",
            field=models.BooleanField(
                default=False,
                help_text="Response values were estimated using a digital ruler or other methods",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="variance_type",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "NA"), (1, "SD"), (2, "SE"), (3, "NR")], default=1
            ),
        ),
        migrations.AlterField(
            model_name="endpointgroup",
            name="lower_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for lower-confidence interval",
                null=True,
                verbose_name="Lower CI",
            ),
        ),
        migrations.AlterField(
            model_name="endpointgroup",
            name="significance_level",
            field=models.FloatField(
                blank=True,
                default=None,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(1),
                ],
                verbose_name="Statistical significance level",
            ),
        ),
        migrations.AlterField(
            model_name="endpointgroup",
            name="significant",
            field=models.BooleanField(
                default=False, verbose_name="Statistically significant from control"
            ),
        ),
        migrations.AlterField(
            model_name="endpointgroup",
            name="upper_ci",
            field=models.FloatField(
                blank=True,
                help_text="Numerical value for upper-confidence interval",
                null=True,
                verbose_name="Upper CI",
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="cas",
            field=models.CharField(
                blank=True,
                help_text="CAS number for chemical-tested, if available.",
                max_length=40,
                verbose_name="Chemical identifier (CAS)",
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="chemical",
            field=models.CharField(blank=True, max_length=128, verbose_name="Chemical name"),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="chemical_source",
            field=models.CharField(blank=True, max_length=128, verbose_name="Source of chemical"),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Text-description of the experimental protocol used. May also include information such as animal husbandry. Note that dosing-regime information and animal details are captured in other fields.",
                verbose_name="Description and animal husbandry",
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="diet",
            field=models.TextField(blank=True, help_text="Description of animal-feed, if relevant"),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="guideline_compliance",
            field=models.CharField(
                blank=True,
                help_text="Description of any compliance methods used (i.e. use of EPA\n            OECD, NTP, or other guidelines; conducted under GLP guideline\n            conditions, non-GLP but consistent with guideline study, etc.)",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="litter_effect_notes",
            field=models.CharField(
                blank=True,
                help_text="Any additional notes describing how litter effects were controlled",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="litter_effects",
            field=models.CharField(
                choices=[
                    ("NA", "Not-applicable"),
                    ("NR", "Not-reported"),
                    ("YS", "Yes, statistical controls"),
                    ("YD", "Yes, study-design"),
                    ("N", "No"),
                    ("O", "Other"),
                ],
                default="NA",
                help_text="Type of controls used for litter-effects",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="name",
            field=models.CharField(
                help_text="Short-text used to describe the experiment (i.e. 2-year cancer bioassay, 28-day inhalation, etc.).",
                max_length=80,
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="purity",
            field=models.FloatField(
                blank=True,
                help_text="Percentage (ex: 95%)",
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0),
                    django.core.validators.MaxValueValidator(100),
                ],
                verbose_name="Chemical purity (%)",
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="purity_available",
            field=models.BooleanField(default=True, verbose_name="Chemical purity available?"),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="type",
            field=models.CharField(
                choices=[
                    ("Ac", "Acute (<24 hr)"),
                    ("St", "Short-term (1-30 days)"),
                    ("Sb", "Subchronic (30-90 days)"),
                    ("Ch", "Chronic (>90 days)"),
                    ("Ca", "Cancer"),
                    ("Me", "Mechanistic"),
                    ("Rp", "Reproductive"),
                    ("Dv", "Developmental"),
                    ("Ot", "Other"),
                    ("NR", "Not-reported"),
                ],
                help_text="Type of study being performed; be as specific as-possible",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="vehicle",
            field=models.CharField(
                blank=True,
                help_text="If a vehicle was used, vehicle common-name",
                max_length=64,
                verbose_name="Chemical vehicle",
            ),
        ),
    ]
