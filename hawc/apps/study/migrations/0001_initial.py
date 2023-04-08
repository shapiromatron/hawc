from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0001_initial"),
        ("contenttypes", "0001_initial"),
        ("lit", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
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
                ("attachment", models.FileField(upload_to=b"study-attachment")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Study",
            fields=[
                (
                    "reference_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="lit.Reference",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "study_type",
                    models.PositiveSmallIntegerField(
                        help_text=b"Type of data captured in the selected study. This determines which fields are required for data-extraction.",
                        choices=[
                            (0, b"Animal Bioassay"),
                            (1, b"Epidemiology"),
                            (4, b"Epidemiology meta-analysis/pooled analysis"),
                            (2, b"In vitro"),
                            (3, b"Other"),
                        ],
                    ),
                ),
                (
                    "short_citation",
                    models.CharField(
                        help_text=b"How the study should be identified (i.e. Smith et al. (2012), etc.)",
                        max_length=256,
                    ),
                ),
                (
                    "full_citation",
                    models.TextField(help_text=b"Complete study citation, in desired format."),
                ),
                (
                    "coi_reported",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text=b"Was a conflict of interest reported by the study authors?",
                        verbose_name=b"COI reported",
                        choices=[
                            (0, b"Authors report they have no COI"),
                            (1, b"Authors disclosed COI"),
                            (2, b"Unknown"),
                            (3, b"Not reported"),
                        ],
                    ),
                ),
                (
                    "coi_details",
                    models.TextField(
                        help_text=b"Details related to potential or disclosed conflict(s) of interest",
                        verbose_name=b"COI details",
                        blank=True,
                    ),
                ),
                ("funding_source", models.TextField(blank=True)),
                (
                    "study_identifier",
                    models.CharField(
                        help_text=b'Reference descriptor for assessment-tracking purposes (for example, "{Author, year, #EndnoteNumber}")',
                        max_length=128,
                        verbose_name=b"Internal study identifier",
                        blank=True,
                    ),
                ),
                (
                    "contact_author",
                    models.BooleanField(
                        default=False,
                        help_text=b"Was the author contacted for clarification of methods or results?",
                    ),
                ),
                (
                    "ask_author",
                    models.TextField(
                        help_text=b"Details on correspondence between data-extractor and author, if needed.",
                        verbose_name=b"Correspondence details",
                        blank=True,
                    ),
                ),
                (
                    "published",
                    models.BooleanField(
                        default=False,
                        help_text=b"If True, this study, risk-of-bias, and extraction details may be visible to reviewers and/or the general public (if assessment-permissions allow this level of visibility). Team-members and project-management can view both published and unpublished studies.",
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        help_text=b"Study summary or details on data-extraction needs.",
                        verbose_name=b"Summary and/or extraction comments",
                        blank=True,
                    ),
                ),
            ],
            options={"ordering": ("short_citation",), "verbose_name_plural": "Studies"},
            bases=("lit.reference",),
        ),
        migrations.CreateModel(
            name="StudyQuality",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "score",
                    models.PositiveSmallIntegerField(
                        default=4,
                        choices=[
                            (1, b"Definitely high risk of bias"),
                            (2, b"Probably high risk of bias"),
                            (3, b"Probably low risk of bias"),
                            (4, b"Definitely low risk of bias"),
                            (0, b"Not applicable"),
                        ],
                    ),
                ),
                ("notes", models.TextField(default=b"", blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "content_type",
                    models.ForeignKey(to="contenttypes.ContentType", on_delete=models.CASCADE),
                ),
            ],
            options={
                "ordering": ("content_type", "object_id", "metric"),
                "verbose_name_plural": "Study Qualities",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="StudyQualityDomain",
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
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField(default=b"")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        related_name="sq_domains",
                        to="assessment.Assessment",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ("pk",)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="StudyQualityMetric",
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
                ("metric", models.CharField(max_length=256)),
                (
                    "description",
                    models.TextField(
                        help_text=b"HTML text describing scoring of this field.",
                        blank=True,
                    ),
                ),
                (
                    "required_animal",
                    models.BooleanField(
                        default=True,
                        help_text=b"Is this metric required for animal bioassay studies?",
                        verbose_name=b"Required for bioassay?",
                    ),
                ),
                (
                    "required_epi",
                    models.BooleanField(
                        default=True,
                        help_text=b"Is this metric required for human epidemiological studies?",
                        verbose_name=b"Required for epidemiology?",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "domain",
                    models.ForeignKey(
                        related_name="metrics",
                        to="study.StudyQualityDomain",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ("domain", "id")},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="studyqualitydomain",
            unique_together=set([("assessment", "name")]),
        ),
        migrations.AddField(
            model_name="studyquality",
            name="metric",
            field=models.ForeignKey(
                related_name="qualities", to="study.StudyQualityMetric", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="studyquality",
            unique_together=set([("content_type", "object_id", "metric")]),
        ),
        migrations.AddField(
            model_name="attachment",
            name="study",
            field=models.ForeignKey(
                related_name="attachments", to="study.Study", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
