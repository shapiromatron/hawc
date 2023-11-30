from typing import Self

from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail import blocks, fields
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.search import index

from ..common.crumbs import Breadcrumb
from . import constants


class TableOfContentsBlock(blocks.StructBlock):
    child_header = blocks.CharBlock(default="Content")
    show_all_descendants = blocks.BooleanBlock(default=False, required=False)

    class Meta:
        template = "docs/blocks/table_of_contents.html"


class AlertBlock(blocks.StructBlock):
    type = blocks.ChoiceBlock(
        choices=[
            ("info", "Info"),
            ("warning", "Warning"),
            ("success", "Success"),
            ("danger", "Danger"),
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("light", "Light"),
            ("dark", "Dark"),
        ],
        default="info",
    )
    label = blocks.CharBlock(required=False)
    message = blocks.RichTextBlock(features=constants.RICH_TEXT_FEATURES)

    class Meta:
        template = "docs/blocks/alert.html"


class DocumentationPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "docs.DocumentationPage", related_name="docs", on_delete=models.CASCADE
    )


class DocumentationPage(Page):
    tagline = models.CharField(max_length=256)
    body = fields.StreamField(
        [
            (
                "content",
                blocks.RichTextBlock(features=constants.RICH_TEXT_FEATURES),
            ),
            (
                "alert",
                AlertBlock(),
            ),
            (
                "toc",
                TableOfContentsBlock(label="Table of Contents"),
            ),
        ],
        block_counts={
            "toc": {"max_num": 1},
            "content": {"max_num": 100},
            "alert": {"max_num": 100},
        },
        use_json_field=True,
    )
    tags = ClusterTaggableManager(through=DocumentationPageTag, blank=True)

    search_fields = [
        *Page.search_fields,
        index.SearchField("tagline"),
    ]

    content_panels = [
        *Page.content_panels,
        FieldPanel("tagline"),
        FieldPanel("tags"),
        FieldPanel("body"),
    ]

    subpage_types = ["DocumentationPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        ancestors = list(self.get_ancestors(inclusive=True).live())[1:]
        context.update(
            breadcrumbs=[Breadcrumb(name=page.title, url=page.url) for page in ancestors],
        )
        return context

    def toc_children(self) -> models.QuerySet:
        return self.get_children().filter(live=True)

    def toc_descendants(self) -> list[Self]:
        desc = self.get_descendants().filter(live=True)
        for page in desc:
            page.indent_offset = page.depth - (self.depth + 1)
        return desc
