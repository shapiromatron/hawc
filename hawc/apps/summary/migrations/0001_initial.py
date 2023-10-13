from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0001_initial"),
        ("assessment", "0001_initial"),
        ("study", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataPivot",
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
                    "title",
                    models.CharField(
                        help_text=b"Enter the title of the visualization (spaces and special-characters allowed).",
                        max_length=128,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text=b"The URL (web address) used to describe this object (no spaces or special-characters).",
                        verbose_name=b"URL Name",
                    ),
                ),
                (
                    "settings",
                    models.TextField(
                        default=b"undefined",
                        help_text=b'Paste content from a settings file from a different data-pivot, or keep set to "undefined".',
                    ),
                ),
                ("caption", models.TextField(default=b"")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("title",)},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DataPivotQuery",
            fields=[
                (
                    "datapivot_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="summary.DataPivot",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "evidence_type",
                    models.PositiveSmallIntegerField(
                        default=0,
                        choices=[
                            (0, b"Animal Bioassay"),
                            (1, b"Epidemiology"),
                            (4, b"Epidemiology meta-analysis/pooled analysis"),
                            (2, b"In vitro"),
                            (3, b"Other"),
                        ],
                    ),
                ),
                ("prefilters", models.TextField(default=b"{}")),
                (
                    "published_only",
                    models.BooleanField(
                        default=True,
                        help_text=b'Only present data from studies which have been marked as "published" in HAWC.',
                        verbose_name=b"Published studies only",
                    ),
                ),
                (
                    "units",
                    models.ForeignKey(
                        blank=True,
                        to="animal.DoseUnits",
                        help_text=b"If kept-blank, dose-units will be random for each endpoint presented. This setting may used for comparing percent-response, where dose-units are not needed.",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={},
            bases=("summary.datapivot",),
        ),
        migrations.CreateModel(
            name="DataPivotUpload",
            fields=[
                (
                    "datapivot_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="summary.DataPivot",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        help_text=b"The data should be in unicode-text format, tab delimited (this is a standard output type in Microsoft Excel).",
                        upload_to=b"data_pivot",
                    ),
                ),
            ],
            options={},
            bases=("summary.datapivot",),
        ),
        migrations.CreateModel(
            name="SummaryText",
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
                ("path", models.CharField(unique=True, max_length=255)),
                ("depth", models.PositiveIntegerField()),
                ("numchild", models.PositiveIntegerField(default=0)),
                ("title", models.CharField(max_length=128)),
                (
                    "slug",
                    models.SlugField(
                        help_text=b"The URL (web address) used on the website to describe this object (no spaces or special-characters).",
                        unique=True,
                        verbose_name=b"URL Name",
                    ),
                ),
                ("text", models.TextField(default=b"")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(to="assessment.Assessment", on_delete=models.CASCADE),
                ),
            ],
            options={"verbose_name_plural": "Summary Text Descriptions"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Visual",
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
                ("title", models.CharField(max_length=128)),
                (
                    "slug",
                    models.SlugField(
                        help_text=b"The URL (web address) used to describe this object (no spaces or special-characters).",
                        verbose_name=b"URL Name",
                    ),
                ),
                (
                    "visual_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, b"animal bioassay endpoint aggregation"),
                            (1, b"animal bioassay endpoint crossview"),
                            (2, b"risk of bias heatmap"),
                            (3, b"risk of bias barchart"),
                        ]
                    ),
                ),
                ("prefilters", models.TextField(default=b"{}")),
                ("settings", models.TextField(default=b"{}")),
                ("caption", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        related_name="visuals", to="assessment.Assessment", on_delete=models.CASCADE
                    ),
                ),
                (
                    "dose_units",
                    models.ForeignKey(
                        blank=True, to="animal.DoseUnits", null=True, on_delete=models.CASCADE
                    ),
                ),
                (
                    "endpoints",
                    models.ManyToManyField(
                        help_text=b"Endpoints to be included in visualization",
                        related_name="visuals",
                        null=True,
                        to="assessment.BaseEndpoint",
                        blank=True,
                    ),
                ),
                (
                    "studies",
                    models.ManyToManyField(
                        help_text=b"Studies to be included in visualization",
                        related_name="visuals",
                        null=True,
                        to="study.Study",
                        blank=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="visual",
            unique_together=set([("assessment", "slug")]),
        ),
        migrations.AlterUniqueTogether(
            name="summarytext",
            unique_together=set([("assessment", "slug"), ("assessment", "title")]),
        ),
        migrations.AddField(
            model_name="datapivot",
            name="assessment",
            field=models.ForeignKey(to="assessment.Assessment", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="datapivot",
            unique_together=set([("assessment", "slug")]),
        ),
    ]
