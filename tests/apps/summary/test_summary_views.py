import json

import pytest

from hawc.apps.summary import forms, models


def clean_json(json_dump):
    remove_fields = ["created", "last_updated", "slug", "text", "assessment"]
    for node in json_dump:
        node.pop("id")
        for field in remove_fields:
            node["data"].pop(field)
        if node.get("children"):
            clean_json(node["children"])


def comparableTree(root):
    tree_form = models.SummaryText.dump_bulk(root)
    clean_json(tree_form)
    return json.dumps(tree_form)


@pytest.mark.skip(reason="TODO: fix")
@pytest.mark.django_db
def test_summary_text_adding_texts(assessment_data):
    # setup
    assessment_working = assessment_data["assessment"]["assessment_working"]

    root = models.SummaryText.get_assessment_root_node(assessment_working.id)
    form = forms.SummaryTextForm(
        {"title": "lvl_1a", "slug": "lvl_1a", "text": "text", "parent": str(root.id)},
        parent=assessment_working,
    )
    assert form.is_valid() is True

    lvl_1a = models.SummaryText.create(form)

    form = forms.SummaryTextForm(
        {"title": "lvl_1b", "slug": "lvl_1b", "text": "text", "sibling": str(lvl_1a.id)},
        parent=assessment_working,
    )
    assert form.is_valid() is True

    form = forms.SummaryTextForm(
        {"title": "lvl_2a", "slug": "lvl_2a", "text": "text", "parent": str(lvl_1a.id)},
        parent=assessment_working,
    )
    assert form.is_valid() is True
    lvl_2a = models.SummaryText.create(form)

    form = forms.SummaryTextForm(
        {"title": "lvl_2b", "slug": "lvl_2b", "text": "text", "sibling": str(lvl_2a.id)},
        parent=assessment_working,
    )
    assert form.is_valid() is True
    lvl_2b = models.SummaryText.create(form)
    assert (
        comparableTree(root)
        == """[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2a"}}, {"data": {"title": "lvl_2b"}}]}, {"data": {"title": "lvl_1b"}}]}]"""
    )

    # Swap 2a and 2b
    lvl_2b.move_st(parent=lvl_1a, sibling=None)
    assert (
        comparableTree(root)
        == """[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2b"}}, {"data": {"title": "lvl_2a"}}]}, {"data": {"title": "lvl_1b"}}]}]"""
    )

    # Swap back
    lvl_2b.move_st(parent=lvl_1a, sibling=lvl_2a)
    assert (
        comparableTree(root)
        == """[{"data": {"title": "assessment-1"}, "children": [{"data": {"title": "lvl_1a"}, "children": [{"data": {"title": "lvl_2a"}}, {"data": {"title": "lvl_2b"}}]}, {"data": {"title": "lvl_1b"}}]}]"""
    )


class TestVisualViews:
    pass
