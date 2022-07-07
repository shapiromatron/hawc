import pytest

from hawc.apps.lit import models
from hawc.refml import tags


@pytest.mark.django_db
def test_build_tree_node_dict(db_keys):
    tree = models.ReferenceFilterTag.get_all_tags(db_keys.assessment_final)
    node_dict = tags.build_tree_node_dict(tree)

    root = models.ReferenceFilterTag.get_assessment_root(db_keys.assessment_final)
    node_list = models.ReferenceFilterTag.get_annotated_list(root)

    # Make sure the built dict has the expected number of entries
    assert len(node_dict) == len(node_list)


@pytest.mark.django_db
def test_create_df(db_keys):
    tree = models.ReferenceFilterTag.get_all_tags(db_keys.assessment_final)
    tag_qs = models.ReferenceTags.objects.assessment_qs(db_keys.assessment_final)

    node_dict = tags.build_tree_node_dict(tree)
    df = tags.create_df(tag_qs, node_dict)

    # Make sure the dataframe has the expected number of rows
    assert len(df) == len(tag_qs)
