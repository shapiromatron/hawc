from django.db import models
from wagtail import fields as wag_fields
from wagtail import models as wag_models
from wagtail.admin.panels import FieldPanel
from wagtail.search import index


class DocsIndexPage(wag_models.Page):
    intro = wag_fields.RichTextField(blank=True)

    content_panels = wag_models.Page.content_panels + [FieldPanel("intro")]


class DocsPage(wag_models.Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = wag_fields.RichTextField(blank=True)

    search_fields = wag_models.Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    content_panels = wag_models.Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]
