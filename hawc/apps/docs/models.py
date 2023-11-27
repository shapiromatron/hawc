from django.db import models
from wagtail import fields as wag_fields
from wagtail import models as wag_models
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from ..common.crumbs import Breadcrumb


class DocsPage(wag_models.Page):
    intro = models.CharField(max_length=250, blank=True)
    body = wag_fields.RichTextField(blank=True)

    search_fields = [
        *wag_models.Page.search_fields,
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    content_panels = [
        *wag_models.Page.content_panels,
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    subpage_types = ["DocsPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        dump_bulk = self.dump_bulk(self)

        def _remove_unpublished(node: dict):
            if "children" in node:
                node["children"] = [child for child in node["children"] if child["data"]["live"]]
                for child in node["children"]:
                    _remove_unpublished(child)

        _remove_unpublished(dump_bulk[0])
        context["node"] = dump_bulk[0]
        ancestors = list(self.get_ancestors().live())[1:]
        context["breadcrumbs"] = [
            *[Breadcrumb(name=page.title, url=page.url) for page in ancestors],
            Breadcrumb(name=self.title),
        ]
        return context
