import pandas as pd
from django.db.models import QuerySet
from django.utils.html import strip_tags

from ..common.helper import FlatFileExporter
from . import models


class ReferenceFlatComplete(FlatFileExporter):
    """
    Returns an export of both references and reference tags
    """

    def _get_header_row(self):
        headers = [
            "HAWC ID",
            "HERO ID",
            "PubMed ID",
            "DOI",
            "Citation",
            "Full Citation",
            "Title",
            "Authors",
            "Authors short",
            "Year",
            "Journal",
            "Abstract",
            "Full text URL",
            "Created",
            "Last updated",
        ]
        if self.kwargs.get("user_tags", False):
            headers.extend(
                [
                    "User Tag ID",
                    "User Tag Author ID",
                    "User Tag Author",
                    "User Tags Resolved",
                    "User Tags Last Updated",
                ]
            )

        headers.extend(models.ReferenceFilterTag.get_flattened_taglist(self.kwargs["tags"]))
        return headers

    def _get_reference_data(self, ref: models.Reference) -> list:
        return [
            ref.pk,
            ref.hero_id,
            ref.pubmed_id,
            ref.doi,
            ref.ref_short_citation,
            ref.ref_full_citation,
            ref.title,
            ref.authors,
            ref.authors_short,
            ref.year,
            ref.journal,
            strip_tags(ref.abstract),
            ref.full_text_url,
            ref.created,
            ref.last_updated,
        ]

    def _get_data_rows(self) -> list[list]:
        tag_tree = models.ReferenceFilterTag.get_tree_descendants(self.kwargs["tags"])
        user_tags = self.kwargs.get("user_tags", False)
        func = self._get_reference_rows_with_users if user_tags else self._get_reference_rows
        return func(tag_tree)

    def _get_reference_rows(
        self, tag_tree: models.ReferenceFilterTag.TreeDescendantType
    ) -> list[list]:
        rows = []
        for ref in self.queryset:
            row = self._get_reference_data(ref)
            reference_tags = set(tag.id for tag in ref.tags.all())
            # for each tag in tree, check to see if this item has been tagged with this
            # tag or its descendants
            row.extend(
                [any(tag in tag_set for tag in reference_tags) for tag_set in tag_tree.values()]
            )
            rows.append(row)
        return rows

    def _get_reference_rows_with_users(
        self, tag_tree: models.ReferenceFilterTag.TreeDescendantType
    ) -> list[list]:
        rows = []
        for user_tag in self.queryset:
            row = self._get_reference_data(user_tag.reference)
            row.extend(
                [
                    user_tag.id,
                    user_tag.user.id,
                    user_tag.user.get_full_name(),
                    user_tag.is_resolved,
                    user_tag.last_updated,
                ]
            )
            user_tags_applied = set(tag.id for tag in user_tag.tags.all())
            # for each tag in tree, check to see if this item has been tagged with this
            # tag or its descendants
            row.extend(
                [any(tag in tag_set for tag in user_tags_applied) for tag_set in tag_tree.values()]
            )
            rows.append(row)
        return rows


class TableBuilderFormat(FlatFileExporter):
    """Format for importing into Table builder."""

    def _get_header_row(self):
        return [
            "PubMed ID",
            "Name",
            "Full Citation",
            "Other URL",
            "PDF URL",
        ]

    def _get_data_rows(self):
        return [
            [
                ref.pubmed_id,
                ref.ref_short_citation,
                ref.ref_full_citation,
                None,
                ref.full_text_url,
            ]
            for ref in self.queryset
        ]


def _long_export(qs: QuerySet, assessment_id: int) -> pd.DataFrame:
    """
    One row per reference-tag combination, including references with no tag.

    Args:
        qs (QuerySet): A Reference queryset
        assessment_id (int): Assessment ID
    """

    tags = models.ReferenceFilterTag.as_dataframe(assessment_id).rename(
        columns=dict(name="tag_name", nested_name="tag_nested_name")
    )
    refs = (
        pd.DataFrame(
            qs.filter(assessment=assessment_id)
            .with_identifiers()
            .values("id", "pubmed_id", "hero_id", "doi", "authors_short", "year", "title")
        )
        .rename(columns=dict(authors_short="authors"))
        .astype(
            dict(
                year=pd.Int64Dtype(),
                pubmed_id=pd.Int64Dtype(),
                hero_id=pd.Int64Dtype(),
            )
        )
    )
    ref_tags = pd.DataFrame(
        models.Reference.objects.tag_pairs(
            models.Reference.objects.filter(assessment=assessment_id)
        )
    )
    return (
        refs.merge(
            ref_tags.merge(tags, left_on="tag_id", right_on="id", how="left").drop(
                columns=["id", "depth"]
            ),
            left_on="id",
            right_on="reference_id",
            how="left",
        )
        .drop(columns=["reference_id"])
        .astype(dict(tag_id=pd.Int64Dtype()))
    )


class ReferenceTagLongExport(FlatFileExporter):
    def build_df(self) -> pd.DataFrame:
        return _long_export(qs=self.queryset, assessment_id=self.kwargs["assessment"].id)
