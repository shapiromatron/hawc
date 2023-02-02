from django.utils.html import strip_tags

from ..common.helper import FlatFileExporter
from . import models


class ReferenceFlatComplete(FlatFileExporter):
    """
    Returns an export of both references and reference tags
    """

    def _reference_data_rows(self, ref: models.Reference) -> list:
        pass

    def _get_header_row(self):
        user_tags = self.kwargs.get("user_tags", False)
        tags = self.kwargs["tags"]
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
        if user_tags:
            headers.extend(
                [
                    "User Tag ID",
                    "User Tag Author ID",
                    "User Tag Author",
                    "User Tags Resolved",
                    "User Tags Last Updated",
                ]
            )

        headers.extend(models.ReferenceFilterTag.get_flattened_taglist(tags))
        return headers

    def _get_reference_data(self, ref: models.Reference) -> list:
        return [
            ref.pk,
            ref.get_hero_id(),
            ref.get_pubmed_id(),
            ref.get_doi_id(),
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

    def _get_data_rows(self):
        user_tags = self.kwargs.get("user_tags", False)
        tag_tree = models.ReferenceFilterTag.get_tree_descendants(self.kwargs["tags"])
        rows = []
        if user_tags:
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
                row.extend(
                    [
                        any(uta in ancestors for uta in user_tags_applied)
                        for ancestors in tag_tree.values()
                    ]
                )
                rows.append(row)
        else:
            for ref in self.queryset:
                row = self._get_reference_data(ref)
                reference_tags = set(tag.id for tag in ref.tags.all())
                row.extend(
                    [
                        any(ref_tag in ancestors for ref_tag in reference_tags)
                        for ancestors in tag_tree.values()
                    ]
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
                ref.get_pubmed_id(),
                ref.ref_short_citation,
                ref.ref_full_citation,
                None,
                ref.full_text_url,
            ]
            for ref in self.queryset
        ]
