import pytest

from hawc.apps.summary.models import SummaryText
from hawc.apps.summary.serializers import SummaryTextSerializer


@pytest.mark.django_db
class TestSummarySerializer:
    @staticmethod
    def comparable_tree(root):
        def _clean_node(nodes):
            remove_fields = ["created", "last_updated", "slug", "text", "assessment"]
            for node in nodes:
                node.pop("id")
                for field in remove_fields:
                    node["data"].pop(field)
                if node.get("children"):
                    _clean_node(node["children"])

        tree = SummaryText.dump_bulk(root)
        _clean_node(tree)
        return tree

    def test_summary_text_swap(self, db_keys):
        # setup
        assessment_id = db_keys.assessment_working
        root = SummaryText.get_assessment_root_node(assessment_id)

        data = {
            "assessment": assessment_id,
            "title": "lvl_1a",
            "slug": "lvl_1a",
            "text": "text",
            "parent": root.id,
            "sibling": None,
        }
        serializer = SummaryTextSerializer(data=data)
        assert serializer.is_valid()
        lvl_1a = serializer.save()

        data.update(title="lvl_1b", slug="lvl_1b", sibling=lvl_1a.id)
        serializer = SummaryTextSerializer(data=data)
        assert serializer.is_valid()
        lvl_1b = serializer.save()

        assert self.comparable_tree(root) == [
            {
                "data": {"title": "assessment-1"},
                "children": [{"data": {"title": "lvl_1a"}}, {"data": {"title": "lvl_1b"}}],
            }
        ]

        # Swap 1a and 1b
        data.update(sibling=None)
        serializer = SummaryTextSerializer(instance=lvl_1b, data=data)
        assert serializer.is_valid()
        serializer.save()
        assert self.comparable_tree(root) == [
            {
                "data": {"title": "assessment-1"},
                "children": [{"data": {"title": "lvl_1b"}}, {"data": {"title": "lvl_1a"}}],
            }
        ]
