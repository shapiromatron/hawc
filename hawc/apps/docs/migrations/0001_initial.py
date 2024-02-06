# Generated by Django 4.2.7 on 2023-11-29 21:53

import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


def setup(apps, schema_editor):
    # Get models
    Permission = apps.get_model("auth", "Permission")
    Group = apps.get_model("auth", "Group")
    ContentType = apps.get_model("contenttypes", "ContentType")
    GroupPagePermission = apps.get_model("wagtailcore", "GroupPagePermission")
    Page = apps.get_model("wagtailcore", "Page")
    Site = apps.get_model("wagtailcore", "Site")
    DocumentationPage = apps.get_model("docs", "DocumentationPage")
    Locale = apps.get_model("wagtailcore", "Locale")
    PageViewRestriction = apps.get_model("wagtailcore", "PageViewRestriction")

    # Delete default wagtail information
    Page.objects.all().delete()
    Locale.objects.all().delete()
    Site.objects.all().delete()

    # Get content type for docs page model
    locale = Locale.objects.create(language_code="en")
    root = Page.objects.create(
        # Page fields
        title="Root",
        slug="",
        content_type=ContentType.objects.get_for_model(Page),
        path="0001",
        depth=1,
        numchild=1,
        url_path="/",
        locale=locale,
    )
    PageViewRestriction.objects.create(page=root, restriction_type="login", password="")

    home = DocumentationPage.objects.create(
        # Page fields
        title="HAWC Documentation",
        draft_title="HAWC Documentation",
        slug="home",
        content_type=ContentType.objects.get_for_model(DocumentationPage),
        path="00010001",
        depth=2,
        numchild=0,
        url_path="/home/",
        locale=locale,
        # DocumentationPage fields
        tagline="HAWC Documentation homepage and for all things HAWC. User's guide, tutorials, etc.",
        body=[
            {
                "type": "content",
                "value": """<p data-block-key="xi8dg">Welcome to the <a href="/">HAWC</a> documentation!</p>""",
                "id": "9cd2f6cf-39e4-4a1b-a44f-7150986568d5",
            },
            {
                "type": "alert",
                "value": {
                    "type": "info",
                    "label": "Example alert",
                    "message": """<p data-block-key="3zi3n">An example alert box!</p>""",
                },
                "id": "cf9f1edb-7c1a-4b9e-8b93-8df40a5d154a",
            },
            {
                "type": "content",
                "value": """<p data-block-key="xi8dg">Add more content here.</p>""",
                "id": "3b848cba-da7a-48c9-8f38-711c20a94cd5",
            },
        ],
    )
    Site.objects.create(hostname="localhost", root_page=home, is_default_site=True)

    editors = Group.objects.get(name="Editors")
    moderators = Group.objects.get(name="Moderators")
    perms = ["add_page", "change_page", "lock_page", "publish_page", "unlock_page"]
    perm_map = {key: Permission.objects.get(codename=key) for key in perms}
    group_page_permissions = [
        GroupPagePermission(page=home, group=editors, permission=perm_map["add_page"]),
        GroupPagePermission(page=home, group=editors, permission=perm_map["change_page"]),
        GroupPagePermission(page=home, group=moderators, permission=perm_map["add_page"]),
        GroupPagePermission(page=home, group=moderators, permission=perm_map["change_page"]),
        GroupPagePermission(page=home, group=moderators, permission=perm_map["lock_page"]),
        GroupPagePermission(page=home, group=moderators, permission=perm_map["publish_page"]),
        GroupPagePermission(page=home, group=moderators, permission=perm_map["unlock_page"]),
    ]
    GroupPagePermission.objects.bulk_create(group_page_permissions)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("taggit", "0005_auto_20220424_2025"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentationPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("tagline", models.CharField(max_length=256)),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            (
                                "content",
                                wagtail.blocks.RichTextBlock(
                                    features=[
                                        "anchor-identifier",
                                        "h3",
                                        "h4",
                                        "h5",
                                        "h6",
                                        "bold",
                                        "italic",
                                        "link",
                                        "ol",
                                        "ul",
                                        "hr",
                                        "image",
                                        "document-link",
                                    ]
                                ),
                            ),
                            (
                                "alert",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "type",
                                            wagtail.blocks.ChoiceBlock(
                                                choices=[
                                                    ("info", "Info"),
                                                    ("warning", "Warning"),
                                                    ("success", "Success"),
                                                    ("danger", "Danger"),
                                                    ("primary", "Primary"),
                                                    ("secondary", "Secondary"),
                                                    ("light", "Light"),
                                                    ("dark", "Dark"),
                                                ]
                                            ),
                                        ),
                                        (
                                            "label",
                                            wagtail.blocks.CharBlock(required=False),
                                        ),
                                        (
                                            "message",
                                            wagtail.blocks.RichTextBlock(
                                                features=[
                                                    "anchor-identifier",
                                                    "h3",
                                                    "h4",
                                                    "h5",
                                                    "h6",
                                                    "bold",
                                                    "italic",
                                                    "link",
                                                    "ol",
                                                    "ul",
                                                    "hr",
                                                    "image",
                                                    "document-link",
                                                ]
                                            ),
                                        ),
                                    ]
                                ),
                            ),
                            (
                                "toc",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "child_header",
                                            wagtail.blocks.CharBlock(default="Content"),
                                        ),
                                        (
                                            "show_all_descendants",
                                            wagtail.blocks.BooleanBlock(
                                                default=False, required=False
                                            ),
                                        ),
                                    ],
                                    label="Table of Contents",
                                ),
                            ),
                        ],
                        use_json_field=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="DocumentationPageTag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="docs",
                        to="docs.documentationpage",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_items",
                        to="taggit.tag",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="documentationpage",
            name="tags",
            field=modelcluster.contrib.taggit.ClusterTaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="docs.DocumentationPageTag",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.RunPython(setup, reverse_code=migrations.RunPython.noop),
    ]
