from django.db import migrations, models

from ..managers import ReferenceFilterTagManager


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Identifiers",
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
                ("unique_id", models.IntegerField()),
                (
                    "database",
                    models.IntegerField(
                        choices=[(0, b"External link"), (1, b"PubMed"), (2, b"HERO")]
                    ),
                ),
                ("content", models.TextField()),
                ("url", models.URLField(blank=True)),
            ],
            options={"verbose_name_plural": "identifiers"},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PubMedQuery",
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
                ("results", models.TextField(blank=True)),
                ("query_date", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-query_date"],
                "get_latest_by": "query_date",
                "verbose_name_plural": "PubMed Queries",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Reference",
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
                ("title", models.TextField(blank=True)),
                ("authors", models.TextField(blank=True)),
                ("year", models.PositiveSmallIntegerField(null=True, blank=True)),
                ("journal", models.TextField(blank=True)),
                ("abstract", models.TextField(blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "block_id",
                    models.DateTimeField(
                        help_text=b"Used internally for determining when reference was originally added",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "assessment",
                    models.ForeignKey(
                        related_name="references",
                        to="assessment.Assessment",
                        on_delete=models.CASCADE,
                    ),
                ),
                (
                    "identifiers",
                    models.ManyToManyField(
                        related_name="references", to="lit.Identifiers", blank=True
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ReferenceFilterTag",
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
                ("name", models.CharField(max_length=100, verbose_name="Name")),
                ("slug", models.SlugField(max_length=100, verbose_name="Slug")),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ReferenceTags",
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
                ("content_object", models.ForeignKey(to="lit.Reference", on_delete=models.CASCADE)),
                (
                    "tag",
                    models.ForeignKey(
                        related_name="lit_referencetags_items",
                        to="lit.ReferenceFilterTag",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={"abstract": False},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Search",
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
                    "search_type",
                    models.CharField(max_length=1, choices=[(b"s", b"Search"), (b"i", b"Import")]),
                ),
                (
                    "source",
                    models.PositiveSmallIntegerField(
                        help_text=b"Database used to identify literature.",
                        choices=[(0, b"External link"), (1, b"PubMed"), (2, b"HERO")],
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text=b"A brief-description to describe the identified literature.",
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
                    "description",
                    models.TextField(
                        help_text=b"A more detailed description of the literature search or import strategy.",
                        blank=True,
                    ),
                ),
                (
                    "search_string",
                    models.TextField(
                        help_text=b"The search-text used to query an online database. Use colors to separate search-terms (optional)."
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "assessment",
                    models.ForeignKey(
                        related_name="literature_searches",
                        to="assessment.Assessment",
                        on_delete=models.CASCADE,
                    ),
                ),
            ],
            options={
                "ordering": ["-last_updated"],
                "get_latest_by": ("last_updated",),
                "verbose_name_plural": "searches",
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="search",
            unique_together=set([("assessment", "slug"), ("assessment", "title")]),
        ),
        migrations.AddField(
            model_name="reference",
            name="searches",
            field=models.ManyToManyField(related_name="references", to="lit.Search"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="reference",
            name="tags",
            field=ReferenceFilterTagManager(
                to="lit.ReferenceFilterTag",
                through="lit.ReferenceTags",
                blank=True,
                help_text="A comma-separated list of tags.",
                verbose_name="Tags",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="pubmedquery",
            name="search",
            field=models.ForeignKey(to="lit.Search", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="identifiers",
            unique_together=set([("database", "unique_id")]),
        ),
    ]
