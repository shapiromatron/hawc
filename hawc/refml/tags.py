from typing import Any

import pandas as pd
from django.db.models import QuerySet
from pydantic import BaseModel as PydanticModel


class TreeNode(PydanticModel):
    id: int
    name: str
    parent: Any = None  # TreeNode

    @property
    def column_name(self) -> str:
        return f"{self.name} ({self.id})"


TreeNodeDict = dict[int, TreeNode]


def build_tree_node_dict(tree: dict) -> TreeNodeDict:
    """Build a dictionary with tag ids and TreeNode instances.

    Given a dump from django treebeard, create a dictionary of tree-nodes. This data structure
    is useful in finding all parent nodes given any tag by ID.

    Args:
        tree (dict): An export from the django-treebeard, `dump_bulk` command.

    Returns:
        TreeNodeDict: An instance of the tree.
    """
    leaves: TreeNodeDict = {}

    def get_leaves(tag, parent_id=None):
        tag_id = tag["id"]
        parent = leaves[parent_id] if parent_id else None
        leaves[tag_id] = TreeNode(id=tag_id, name=tag["data"]["name"], parent=parent)
        for child in tag.get("children", []):
            get_leaves(child, tag_id)

    # special case for root
    root = tree[0]
    leaves[root["id"]] = TreeNode(id=root["id"], name="assessment-root", parent=None)

    # start at root node's children; since we these effectively have no parents
    for tag in tree[0].get("children", []):
        get_leaves(tag, parent_id=root["id"])

    return leaves


def create_df(tag_qs: QuerySet, tree_dict: TreeNodeDict, sep: str = "|") -> pd.DataFrame:
    """Create a dataframe where rows are each reference ID, and parents are each parent tag with
    values being text-values child-tags, pipe-delimited. Used for building heatmaps.

    Args:
        tag_qs (QuerySet): A queryset of tags from ReferenceTag
        tree_dict (TreeNodeDict): must contain all tag ids in the queryset
        sep (str, optional): When multiple tags with parent, delimiter; defaults to "|".

    Returns:
        pd.DataFrame: the resulting dataframe.
    """
    data = []

    def add_data(ref_id: int, node: TreeNode):
        if node.parent is not None:
            data.append((ref_id, node.parent.column_name, node.name))
            add_data(ref_id, node.parent)

    for reftag in tag_qs:
        add_data(reftag.content_object_id, tree_dict[reftag.tag_id])

    return (
        pd.DataFrame(data=data, columns=("ref_id", "attribute", "value"))
        .drop_duplicates()
        .groupby(["ref_id", "attribute"], as_index=False)
        .agg({"value": sep.join})
        .reset_index()
        .drop(columns=["index"])
        .pivot(index="ref_id", columns="attribute", values="value")
        .reset_index()
        .fillna("")
    )
