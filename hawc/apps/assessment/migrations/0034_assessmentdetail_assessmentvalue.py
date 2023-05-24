import django.db.models.deletion
from django.db import migrations, models

import hawc.apps.common.validators


class Migration(migrations.Migration):
    dependencies = [
        ("study", "0011_auto_20190416_2035"),
        ("assessment", "0033_assessment_admin_notes"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssessmentValue",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "evaluation_type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "Cancer"), (1, "Noncancer"), (2, "Cancer and Noncancer")],
                        default=0,
                        help_text="Substance evaluation conducted",
                    ),
                ),
                (
                    "system",
                    models.CharField(
                        help_text="Identify the health system of concern (e.g., Hepatic, Nervous, Reproductive)",
                        max_length=128,
                        verbose_name="System or health effect basis",
                    ),
                ),
                (
                    "value_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Overall RfD"),
                            (10, "Overall RfC"),
                            (20, "IUR"),
                            (30, "OSF"),
                            (40, "Screening-Level RfD"),
                            (50, "Screening-Level RfC"),
                            (60, "Organ-Specific RfD"),
                            (70, "Organ-Specific RfC"),
                            (100, "Other"),
                        ],
                        help_text="Type of derived value",
                    ),
                ),
                ("value", models.FloatField(help_text="The derived value")),
                ("value_unit", models.CharField(max_length=32, verbose_name="Value units")),
                (
                    "confidence",
                    models.CharField(
                        blank=True, help_text="Confidence in the toxicity value", max_length=64
                    ),
                ),
                (
                    "duration",
                    models.CharField(blank=True, help_text="Duration of value", max_length=128),
                ),
                (
                    "basis",
                    models.TextField(
                        blank=True,
                        help_text="Describe the justification for deriving this value. Information should include the endpoint of concern from the principal study (e.g., decreased embryo/fetal survival) with the appropriate references included (Smith et al. 2023)",
                    ),
                ),
                (
                    "pod_type",
                    models.CharField(
                        blank=True,
                        help_text="Point of departure type, for example, NOAEL, LOAEL, BMDL (10% extra risk)",
                        max_length=32,
                        verbose_name="POD Type",
                    ),
                ),
                (
                    "pod_value",
                    models.FloatField(
                        blank=True,
                        help_text="The Point of Departure (POD)",
                        null=True,
                        verbose_name="POD Value",
                    ),
                ),
                (
                    "pod_unit",
                    models.CharField(
                        blank=True,
                        help_text="Units for the Point of Departure (POD)",
                        max_length=32,
                        verbose_name="POD units",
                    ),
                ),
                (
                    "uncertainty",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (1, "1"),
                            (3, "3"),
                            (10, "10"),
                            (30, "30"),
                            (100, "100"),
                            (300, "300"),
                            (1000, "1,000"),
                            (3000, "3,000"),
                            (10000, "10,000"),
                            (30000, "30,000"),
                            (100000, "100,000"),
                            (300000, "300,000"),
                        ],
                        help_text="Composite uncertainty factor applied to POD to derive the final value",
                        null=True,
                        verbose_name="Uncertainty factor",
                    ),
                ),
                (
                    "tumor_type",
                    models.CharField(
                        blank=True,
                        help_text="Describe the specific types of cancer found within the specific organ system (e.g., tumor site)",
                        max_length=128,
                        verbose_name="Tumor/Cancer type",
                    ),
                ),
                (
                    "extrapolation_method",
                    models.TextField(
                        blank=True,
                        help_text="Describe the statistical method(s) used to derive the cancer toxicity values (e.g., Time-to-tumor dose-response model with linear extrapolation from the POD (BMDL10(HED)) associated with 10% extra cancer risk)",
                    ),
                ),
                (
                    "evidence",
                    models.TextField(
                        blank=True,
                        help_text="Describe the overall characterization of the evidence (e.g., cancer or noncancer descriptors) and the basis for this determination (e.g., based on strong and consistent evidence in animals and humans)",
                        verbose_name="Evidence characterization",
                    ),
                ),
                (
                    "adaf",
                    models.BooleanField(
                        default=False,
                        help_text="Has an Age Dependent Adjustment Factor (ADAF) been applied?",
                        verbose_name="ADAF applied?",
                    ),
                ),
                (
                    "non_adaf_value",
                    models.FloatField(
                        blank=True,
                        help_text="Value without ADAF adjustment (units the same as Value above)",
                        null=True,
                        verbose_name="Non-ADAF adjusted value",
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        blank=True,
                        help_text="General comments related to the derivation of this value",
                    ),
                ),
                (
                    "extra",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text='Any additional custom fields; A <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON">JSON</a> object where keys are strings and values are strings or numbers. For example, <code>{"Player": "Michael Jordan", "Number": 23}</code>.',
                        validators=[hawc.apps.common.validators.FlatJSON.validate],
                        verbose_name="Additional fields",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="values",
                        to="assessment.assessment",
                    ),
                ),
                (
                    "species_studied",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="assessment.species",
                    ),
                ),
                (
                    "study",
                    models.ForeignKey(
                        blank=True,
                        help_text="Link to Key Study in HAWC. If it does not exist or there are multiple studies, leave blank and explain in comments",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="study.study",
                        verbose_name="Key study",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "values",
            },
        ),
        migrations.CreateModel(
            name="AssessmentDetail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "project_type",
                    models.CharField(
                        blank=True,
                        help_text="If part of a product line, the name of the project type",
                        max_length=64,
                    ),
                ),
                (
                    "project_status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Scoping"),
                            (5, "Problem Formulation"),
                            (10, "Internal Review"),
                            (15, "Interagency Review"),
                            (20, "Public Comment"),
                            (25, "External Peer Review"),
                            (30, "Final"),
                            (35, "Other"),
                        ],
                        default=0,
                        help_text="High-level project management milestones for this assessment",
                    ),
                ),
                (
                    "project_url",
                    models.URLField(
                        blank=True,
                        help_text="The URL to an external project page, if one exists",
                        validators=[hawc.apps.common.validators.validate_hyperlink],
                        verbose_name="External Project URL",
                    ),
                ),
                (
                    "peer_review_status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Contract-Led"),
                            (5, "FACA Panel"),
                            (10, "NASEM"),
                            (15, "Journal Review"),
                            (20, "No Review"),
                        ],
                        default=20,
                        help_text="Define the current status of peer review of this assessment, if any",
                        verbose_name="Peer Review Status",
                    ),
                ),
                (
                    "qa_id",
                    models.CharField(
                        blank=True,
                        help_text="Quality Assurance (QA) tracking identifier, if one exists.",
                        max_length=16,
                        verbose_name="Quality Assurance (QA) tracking identifier",
                    ),
                ),
                (
                    "qa_url",
                    models.URLField(
                        blank=True,
                        help_text="Quality Assurance Website, if any",
                        validators=[hawc.apps.common.validators.validate_hyperlink],
                        verbose_name="Quality Assurance (QA) URL",
                    ),
                ),
                (
                    "report_id",
                    models.CharField(
                        blank=True,
                        help_text="A external report number or identifier (e.g., a DOI, publication number)",
                        max_length=64,
                        verbose_name="Report identifier",
                    ),
                ),
                (
                    "report_url",
                    models.URLField(
                        blank=True,
                        help_text="The URL to the final document or publication, if one exists",
                        validators=[hawc.apps.common.validators.validate_hyperlink],
                        verbose_name="External Document URL",
                    ),
                ),
                (
                    "extra",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text='Any additional custom fields; A <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON">JSON</a> object where keys are strings and values are strings or numbers. For example, <code>{"Player": "Michael Jordan", "Number": 23}</code>.',
                        validators=[hawc.apps.common.validators.FlatJSON.validate],
                        verbose_name="Additional fields",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="details",
                        to="assessment.assessment",
                    ),
                ),
            ],
        ),
    ]
