from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assessment",
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
                (
                    "name",
                    models.CharField(
                        help_text=b"Describe the objective of the health-assessment.",
                        max_length=80,
                        verbose_name=b"Assessment Name",
                    ),
                ),
                (
                    "year",
                    models.PositiveSmallIntegerField(
                        help_text=b"Year with which the assessment should be associated.",
                        verbose_name=b"Assessment Year",
                    ),
                ),
                (
                    "version",
                    models.CharField(
                        help_text=b"Version to describe the current assessment (i.e. draft, final, v1).",
                        max_length=80,
                        verbose_name=b"Assessment Version",
                    ),
                ),
                (
                    "cas",
                    models.CharField(
                        help_text=b"Add a single CAS-number if one is available to describe the assessment, otherwise leave-blank.",
                        max_length=40,
                        verbose_name=b"Chemical identifier (CAS)",
                        blank=True,
                    ),
                ),
                (
                    "assessment_objective",
                    models.TextField(
                        help_text=b"Describe the assessment objective(s), research questions, or clarification on the purpose of the assessment.",
                        blank=True,
                    ),
                ),
                (
                    "editable",
                    models.BooleanField(
                        default=True,
                        help_text=b"Project-managers and team-members are allowed to edit assessment components.",
                    ),
                ),
                (
                    "public",
                    models.BooleanField(
                        default=False,
                        help_text=b"The assessment can be viewed by the general public.",
                    ),
                ),
                (
                    "hide_from_public_page",
                    models.BooleanField(
                        default=False,
                        help_text=b"If public, anyone with a link can view, but do not show a link on the public-assessment page.",
                    ),
                ),
                (
                    "enable_literature_review",
                    models.BooleanField(
                        default=True,
                        help_text=b"Search or import references from PubMed and other literature databases, define inclusion, exclusion, or descriptive tags, and apply these tags to retrieved literature for your analysis.",
                    ),
                ),
                (
                    "enable_data_extraction",
                    models.BooleanField(
                        default=True,
                        help_text=b"Extract animal bioassay, epidemiological, or in-vitro data from key references and create customizable, dynamic visualizations or summary data and associated metadata for display.",
                    ),
                ),
                (
                    "enable_study_quality",
                    models.BooleanField(
                        default=True,
                        help_text=b"Define criteria for a systematic review of literature, and apply these criteria to references in your literature-review. View details on findings and identify areas with a potential risk-of-bias.",
                    ),
                ),
                (
                    "enable_bmd",
                    models.BooleanField(
                        default=True,
                        help_text=b"Conduct benchmark dose (BMD) modeling on animal bioassay data available in the HAWC database, using the US EPA's Benchmark Dose Modeling Software (BMDS).",
                        verbose_name=b"Enable BMD modeling",
                    ),
                ),
                (
                    "enable_reference_values",
                    models.BooleanField(
                        default=True,
                        help_text=b"Define a point-of-departure, apply uncertainty factors, and derive reference values by route of exposure.",
                    ),
                ),
                (
                    "enable_summary_text",
                    models.BooleanField(
                        default=True,
                        help_text=b'Create custom-text to describe methodology and results of the assessment; insert tables, figures, and visualizations to using "smart-tags" which link to other data in HAWC.',
                    ),
                ),
                (
                    "enable_comments",
                    models.BooleanField(
                        default=True,
                        help_text=b"Enable comments from reviewers or the general-public on datasets or findings; comment-functionality and visibility can be controlled in advanced-settings.",
                    ),
                ),
                (
                    "conflicts_of_interest",
                    models.TextField(
                        help_text=b"Describe any conflicts of interest by the assessment-team.",
                        blank=True,
                    ),
                ),
                (
                    "funding_source",
                    models.TextField(
                        help_text=b"Describe the funding-source(s) for this assessment.",
                        blank=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "project_manager",
                    models.ManyToManyField(
                        help_text=b"Has complete assessment control, including the ability to add team members, make public, or delete an assessment. You can add multiple project-managers.",
                        related_name="assessment_pms",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reviewers",
                    models.ManyToManyField(
                        help_text=b"Can view the assessment even if the assessment is not public, but cannot add or change content. Reviewers may optionally add comments, if this feature is enabled. You can add multiple reviewers.",
                        related_name="assessment_reviewers",
                        null=True,
                        to=settings.AUTH_USER_MODEL,
                        blank=True,
                    ),
                ),
                (
                    "team_members",
                    models.ManyToManyField(
                        help_text=b"Can view and edit assessment components, if project is editable. You can add multiple team-members",
                        related_name="assessment_teams",
                        null=True,
                        to=settings.AUTH_USER_MODEL,
                        blank=True,
                    ),
                ),
            ],
            options={"ordering": ("-created",)},
            bases=(models.Model,),
        ),
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
                ("object_id", models.PositiveIntegerField()),
                ("title", models.CharField(max_length=128)),
                ("attachment", models.FileField(upload_to=b"attachment")),
                ("publicly_available", models.BooleanField(default=True)),
                ("description", models.TextField(blank=True)),
                (
                    "content_type",
                    models.ForeignKey(to="contenttypes.ContentType", on_delete=models.CASCADE),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BaseEndpoint",
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
                (
                    "name",
                    models.CharField(max_length=128, verbose_name=b"Endpoint name"),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(to="assessment.Assessment", on_delete=models.CASCADE),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ChangeLog",
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
                ("date", models.DateField(unique=True)),
                (
                    "name",
                    models.CharField(
                        help_text=b"Adjective + noun combination",
                        unique=True,
                        max_length=128,
                        verbose_name=b"Release name",
                    ),
                ),
                ("slug", models.SlugField(max_length=128, verbose_name=b"URL slug")),
                (
                    "header",
                    models.TextField(help_text=b"One-paragraph description of major changes made"),
                ),
                (
                    "detailed_list",
                    models.TextField(
                        help_text=b"Detailed bulleted-list of individual item-changes"
                    ),
                ),
            ],
            options={"ordering": ("-date",)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="EffectTag",
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
                ("name", models.CharField(unique=True, max_length=128)),
                (
                    "slug",
                    models.SlugField(
                        help_text=b"The URL (web address) used to describe this object (no spaces or special-characters).",
                        unique=True,
                        max_length=128,
                    ),
                ),
            ],
            options={"ordering": ("name",)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ReportTemplate",
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
                ("description", models.CharField(max_length=256)),
                (
                    "report_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, b"Literature search"),
                            (1, b"Studies and study-quality"),
                            (2, b"Animal bioassay"),
                            (3, b"Epidemiology"),
                            (4, b"Epidemiology meta-analysis/pooled analysis"),
                            (5, b"In vitro"),
                        ]
                    ),
                ),
                ("template", models.FileField(upload_to=b"templates")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        related_name="templates",
                        blank=True,
                        to="assessment.Assessment",
                        on_delete=models.CASCADE,
                        null=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="baseendpoint",
            name="effects",
            field=models.ManyToManyField(
                to="assessment.EffectTag", null=True, verbose_name=b"Tags", blank=True
            ),
            preserve_default=True,
        ),
    ]
