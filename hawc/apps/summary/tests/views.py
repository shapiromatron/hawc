import json

from django.test import TestCase

from hawc.apps.assessment.tests.utils import build_assessments_for_permissions_testing
from hawc.apps.summary import forms, models


class SummaryTextTests(TestCase):
    def setUp(self):
        build_assessments_for_permissions_testing(self)

    @staticmethod
    def clean_json(json_dump):
        remove_fields = ["created", "last_updated", "slug", "text", "assessment"]
        for node in json_dump:
            node.pop("id")
            for field in remove_fields:
                node["data"].pop(field)
            if node.get("children"):
                SummaryTextTests.clean_json(node["children"])

    @staticmethod
    def comparableTree(root):
        tree_form = models.SummaryText.dump_bulk(root)
        SummaryTextTests.clean_json(tree_form)
        return json.dumps(tree_form)

    def test_adding_texts(self):
        root = models.SummaryText.get_assessment_root_node(self.assessment_working.id)
        form = forms.SummaryTextForm(
            {"title": "lvl_1a", "slug": "lvl_1a", "text": "text", "parent": str(root.id)},
            parent=self.assessment_working,
        )
        self.assertTrue(form.is_valid())
        lvl_1a = models.SummaryText.create(form)

        form = forms.SummaryTextForm(
            {"title": "lvl_1b", "slug": "lvl_1b", "text": "text", "sibling": str(lvl_1a.id)},
            parent=self.assessment_working,
        )
        self.assertTrue(form.is_valid())

        form = forms.SummaryTextForm(
            {"title": "lvl_2a", "slug": "lvl_2a", "text": "text", "parent": str(lvl_1a.id)},
            parent=self.assessment_working,
        )
        self.assertTrue(form.is_valid())
        lvl_2a = models.SummaryText.create(form)

        form = forms.SummaryTextForm(
            {"title": "lvl_2b", "slug": "lvl_2b", "text": "text", "sibling": str(lvl_2a.id)},
            parent=self.assessment_working,
        )
        self.assertTrue(form.is_valid())
        lvl_2b = models.SummaryText.create(form)

        self.assertEqual(
            SummaryTextTests.comparableTree(root),
            """[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2a"}}, {"data": {"title": "lvl_2b"}}]}, {"data": {"title": "lvl_1b"}}]}]""",
        )

        # Swap 2a and 2b
        lvl_2b.move_st(parent=lvl_1a, sibling=None)
        self.assertEqual(
            SummaryTextTests.comparableTree(root),
            """[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2b"}}, {"data": {"title": "lvl_2a"}}]}, {"data": {"title": "lvl_1b"}}]}]""",
        )

        # Swap back
        lvl_2b.move_st(parent=lvl_1a, sibling=lvl_2a)
        self.assertEqual(
            SummaryTextTests.comparableTree(root),
            """[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2a"}}, {"data": {"title": "lvl_2b"}}]}, {"data": {"title": "lvl_1b"}}]}]""",
        )
