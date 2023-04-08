# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-11 10:48
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0022_move_fields_delete"),
    ]

    operations = [
        migrations.AlterField(
            model_name="animalgroup",
            name="animal_source",
            field=models.CharField(
                blank=True,
                help_text="Source from where animals were acquired",
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="comments",
            field=models.TextField(
                blank=True,
                help_text="Copy paste animal husbandry information from materials and methods, use quotation marks around all text directly copy/pasted from paper.",
                verbose_name="Animal Source and Husbandry",
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="lifestage_assessed",
            field=models.CharField(
                blank=True,
                help_text="Definitions: <b>Developmental</b>: Prenatal and perinatal exposure in dams or postnatal exposure in offspring until sexual maturity (~6 weeks in rats and mice). Include studies with pre-mating exposure if the endpoint focus is developmental. <b>Adult</b>: Exposure in sexually mature males or females. <b>Adult (gestation)</b>: Exposure in dams during pregnancy. <b>Multi-lifestage</b>: includes both developmental and adult (i.e., multi-generational studies, exposure that start before sexual maturity and continue to adulthood)",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="lifestage_exposed",
            field=models.CharField(
                blank=True,
                help_text="Definitions: <strong>Developmental</strong>: Prenatal and perinatal exposure in dams or postnatal exposure in offspring until sexual maturity (~6 weeks in rats and mice). Include studies with pre-mating exposure <em>if the endpoint focus is developmental</em>. <strong>Adult</strong>: Exposure in sexually mature males or females. <strong>Adult (gestation)</strong>: Exposure in dams duringpregnancy. <strong>Multi-lifestage</strong>: includes both developmental and adult (i.e., multi-generational studies, exposure that start before sexual maturity and continue to adulthood)",
                max_length=32,
                verbose_name="Exposure lifestage",
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="name",
            field=models.CharField(
                help_text="\n            Name should be: sex, common strain name, species (plural) and use Title Style\n            (e.g. Male Sprague Dawley Rat, Female C57BL/6 Mice, Male and Female\n            C57BL/6 Mice). For developmental studies, include the generation before\n            sex in title (e.g., F1 Male Sprague Dawley Rat or P0 Female C57 Mice)\n            ",
                max_length=80,
            ),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="strain",
            field=models.ForeignKey(
                help_text='When adding a new strain, put the stock in parenthesis, e.g., "Sprague-Dawley (Harlan)."',
                on_delete=django.db.models.deletion.CASCADE,
                to="assessment.Strain",
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="description",
            field=models.TextField(
                blank=True,
                help_text='Cut and paste from methods, use quotation marks around all text directly copy/pasted from paper. Also summarize results of any analytical work done to confirm dose, stability, etc. This can be a narrative summary of tabular information, e.g., "Author\'s present data on the target and actual concentration (Table 1; means &plusmn; SD for entire 13-week period) and the values are very close." ',
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="duration_exposure",
            field=models.FloatField(
                blank=True,
                help_text="Length of exposure period (fractions allowed), used for sorting in visualizations. For single-dose or multiple-dose/same day gavage studies, 1.",
                null=True,
                verbose_name="Exposure duration (days)",
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="duration_exposure_text",
            field=models.CharField(
                blank=True,
                help_text='Length of time between start of exposure and outcome assessment, in days when &lt;7 (e.g., 5d), weeks when &ge;7 days to 12 weeks (e.g., 1wk, 12wk), or months when &gt;12 weeks (e.g., 15mon). For repeated measures use descriptions such as "1, 2 and 3 wk".  For inhalations studies, also include hours per day and days per week, e.g., "13wk (6h/d, 7d/wk)." This field is commonly used in visualizations, so use abbreviations (h, d, wk, mon, y) and no spaces between numbers to save space. For reproductive and developmental studies, where possible instead include abbreviated age descriptions such as "GD1-10" or "GD2-PND10". For gavage studies, include the number of doses, e.g. "1wk (1dose/d, 5d/wk)" or "2doses" for a single-day experiment.',
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
                default="VT",
                help_text="Description of negative-controls used",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="dosingregime",
            name="positive_control",
            field=models.NullBooleanField(
                choices=[(True, "Yes"), (False, "No"), (None, "Unknown")],
                default=False,
                help_text="Was a positive control used?",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="data_location",
            field=models.CharField(
                blank=True,
                help_text='Details on where the data are found in the literature (ex: "Figure 1", "Table 2", "Text, p. 24", "Figure 1 and Text, p.24")',
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="diagnostic",
            field=models.TextField(
                blank=True,
                help_text="List the endpoint/adverse outcome name as used in the study. This will help during QA/QC of the extraction to the original study in cases where the endpoint/adverse outcome name is adjusted for consistency across studies or assessments.",
                verbose_name="Endpoint Name in Study",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="endpoint_notes",
            field=models.TextField(
                blank=True,
                help_text="Cut and paste from methods, use quotation marks around all text directly copy/pasted from paper. Include all methods pertinent to measuring ALL outcomes, including statistical methods. This will make it easier to copy from existing HAWC endpoints to create new endpoints for a study.",
                verbose_name="Methods",
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
                    (4, "---"),
                ],
                default=4,
                help_text="Response direction which would be considered adverse",
                verbose_name="Expected response adversity direction",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="monotonicity",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (8, "--"),
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
            name="observation_time_units",
            field=models.PositiveSmallIntegerField(
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
        migrations.AlterField(
            model_name="endpoint",
            name="organ",
            field=models.CharField(
                blank=True,
                help_text="Relevant organ or tissue",
                max_length=128,
                verbose_name="Organ (and tissue)",
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="results_notes",
            field=models.TextField(
                blank=True,
                help_text='\n            Qualitative description of the results. This field can be\n            left blank if there is no need to further describe numerically\n            extracted findings, e.g., organ or body weights. Use this\n            field to describe findings such as the type and severity\n            of histopathology or malformations not otherwise captured\n            in the numerical data extraction. Also use this field to cut\n            and paste findings described only in text in the study. If\n            coding is used to create exposure-response arrays, then add\n            this comment in bold font at the start of the text box entry\n            <strong>"For exposure-response array data display purposes, the following\n            results were coded (control and no effect findings were coded as\n            "0", treatment-related increases were coded as "1", and\n            treatment-related decreases were coded as "-1"."</strong>\n            ',
            ),
        ),
        migrations.AlterField(
            model_name="endpoint",
            name="statistical_test",
            field=models.CharField(
                blank=True,
                help_text="Short description of statistical analysis techniques used, e.g., Fisher Exact Test, ANOVA, Chi Square, Peto's test, none conducted",
                max_length=256,
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="cas",
            field=models.CharField(
                blank=True,
                help_text="\n                CAS number for chemical-tested. Use N/A if not applicable. If more than one\n                CAS number is applicable, then use a common one here and indicate others\n                in the comment field below.\n                ",
                max_length=40,
                verbose_name="Chemical identifier (CAS)",
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="chemical",
            field=models.CharField(
                blank=True,
                help_text="This field may get displayed in visualizations, so consider using a common acronym, e.g., BPA instead of Bisphenol A",
                max_length=128,
                verbose_name="Chemical name",
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Add additional comments. In most cases, this field will be blank. Note that dosing-regime information and animal details are captured in the Animal Group extraction module.",
                verbose_name="Comments",
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="guideline_compliance",
            field=models.CharField(
                blank=True,
                help_text='\n            Description of any compliance methods used (i.e. use of EPA OECD, NTP,\n            or other guidelines; conducted under GLP guideline conditions, non-GLP but consistent\n            with guideline study, etc.). This field response should match any description used\n            in study evaluation in the reporting quality domain, e.g., GLP study (OECD guidelines\n            414 and 412, 1981 versions). If not reported, then use state "not reported."\n            ',
                max_length=128,
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="name",
            field=models.CharField(
                help_text="Short-text used to describe the experiment (i.e. 2-Year Cancer Bioassay, 10-Day Oral, 28-Day Inhalation, etc.) using title style (all words capitalized). If study contains more than one chemical, then also include the chemical name (e.g. 28-Day Oral PFBS).",
                max_length=80,
            ),
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
                    ("1r", "1-generation reproductive"),
                    ("2r", "2-generation reproductive"),
                    ("Dv", "Developmental"),
                    ("Ot", "Other"),
                    ("NR", "Not-reported"),
                ],
                help_text="Type of study being performed; be as specific as possible",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="experiment",
            name="vehicle",
            field=models.CharField(
                blank=True,
                help_text='Describe vehicle (use name as described in methods but also add the common name if the vehicle was described in a non-standard way). Enter "not reported" if the vehicle is not described. For inhalation studies, air can be inferred if not explicitly reported. Examples: "corn oil," "filtered air," "not reported, but assumed clean air."',
                max_length=64,
                verbose_name="Chemical vehicle",
            ),
        ),
    ]
