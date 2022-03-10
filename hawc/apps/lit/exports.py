from copy import copy, deepcopy

from django.utils.html import strip_tags

from ..common.helper import FlatFileExporter
from . import models


class ReferenceFlatComplete(FlatFileExporter):
    """
    Returns an export of both references and reference tags
    """

    def _get_header_row(self):
        tags = self.kwargs.get("tags", None)
        include_parent_tag = self.kwargs.get("include_parent_tag", False)

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
        if tags:
            headers.extend(
                models.ReferenceFilterTag.get_flattened_taglist(tags, include_parent_tag)
            )
        return headers

    def _get_data_rows(self):
        rows = []

        def resetTags(tags):
            def setFalse(obj):
                obj["isTagged"] = False
                for child in obj.get("children", []):
                    setFalse(child)

            tagsCopy = deepcopy(tags)
            setFalse(tagsCopy)
            return tagsCopy

        tags_base = resetTags(self.kwargs.get("tags")[0])
        include_parent_tag = self.kwargs.get("include_parent_tag", False)

        def getTagRow(tags):
            row = []

            def printStatus(obj):
                row.append(obj["isTagged"])
                for child in obj.get("children", []):
                    printStatus(child)

            if include_parent_tag:
                printStatus(tags)
            else:
                for child in tags.get("children", []):
                    printStatus(child)
            return row

        def applyTags(tagslist, ref):
            def applyTag(tagged, tagslist):
                def checkMatch(tagged, tag, parents):
                    parents = copy(parents)
                    if tagged.id == tag["id"]:
                        tag["isTagged"] = True
                        for parent in parents:
                            parent["isTagged"] = True

                    parents.append(tag)
                    for child in tag.get("children", []):
                        checkMatch(tagged, child, parents)

                if include_parent_tag:
                    checkMatch(tagged, tagslist, [])
                else:
                    for child in tagslist.get("children", []):
                        checkMatch(tagged, child, [])

            for tag in ref.tags.all():
                applyTag(tag, tagslist)

        row = []
        for ref in self.queryset:
            row = [
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

            tagsCopy = deepcopy(tags_base)
            applyTags(tagsCopy, ref)
            row.extend(getTagRow(tagsCopy))

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
