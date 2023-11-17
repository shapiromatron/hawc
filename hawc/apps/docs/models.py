from typing import NamedTuple

from django.db import models
from wagtail import fields as wag_fields
from wagtail import models as wag_models
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

from ..common.crumbs import Breadcrumb


class Node(NamedTuple):
    """Tree node."""

    data: object
    children: list["Node"]


class DocsIndexPage(wag_models.Page):
    intro = models.CharField(max_length=250, blank=True)
    body = wag_fields.RichTextField(blank=True)

    content_panels = [
        *wag_models.Page.content_panels,
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    subpage_types = ["DocsIndexPage", "DocsPage"]

    def get_site_tree(self):
        return self.get_tree(self.get_site().root_page)

    def get_nested_tree(self, specific=True, live=True):
        dfs_tree = self.get_tree(self)
        if specific:
            dfs_tree = dfs_tree.specific()
        if live:
            dfs_tree = dfs_tree.live()

        def _traverse_tree(node: Node, next_index: int):
            while next_index < len(dfs_tree):
                if (_next_node := dfs_tree[next_index]).depth > node.data.depth:
                    next_node = Node(data=_next_node, children=[])
                    node.children.append(next_node)
                    next_index = _traverse_tree(next_node, next_index + 1)
                else:
                    return next_index
            return next_index

        root_node = Node(data=self, children=[])
        _traverse_tree(root_node, 1)
        return root_node

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["node"] = self.get_nested_tree()
        ancestors = list(self.get_ancestors().live())[1:]
        context["breadcrumbs"] = [
            *[Breadcrumb(name=page.title, url=page.url) for page in ancestors],
            Breadcrumb(name=self.title),
        ]
        return context


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

    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        ancestors = list(self.get_ancestors().live())[1:]
        context["breadcrumbs"] = [
            *[Breadcrumb(name=page.title, url=page.url) for page in ancestors],
            Breadcrumb(name=self.title),
        ]
        return context
