import re

from django.contrib.postgres.search import SearchVector
from django.db import models

EXTERNAL_LINK = 0


class ReferenceDatabase(models.IntegerChoices):
    MANUAL = 0, "Manually added"
    PUBMED = 1, "PubMed"
    HERO = 2, "HERO"
    RIS = 3, "RIS (EndNote/Reference Manager)"
    DOI = 4, "DOI"
    WOS = 5, "Web of Science"
    SCOPUS = 6, "Scopus"
    EMBASE = 7, "Embase"

    @classmethod
    def import_choices(cls) -> list[tuple[int, str]]:
        return [
            (choice.value, choice.label)
            for choice in [ReferenceDatabase.PUBMED, ReferenceDatabase.HERO]
        ]


class SearchType(models.TextChoices):
    SEARCH = "s", "Search"
    IMPORT = "i", "Import"


class DuplicateResolution(models.IntegerChoices):
    UNRESOLVED = 0, "Unresolved"
    RESOLVED = 1, "Primary identified"  # TODO: change to "primary identified"
    FALSE_POSITIVE = 2, "False positive"


# generalized/adapted from https://www.crossref.org/blog/dois-and-matching-regular-expressions/
DOI_EXACT = re.compile(r"^10\.\d{4,9}/[^\s]+$")
DOI_EXTRACT = re.compile(r"10\.\d{4,9}/[^\s]+")
DOI_EXAMPLE = "10.1234/s123456"

REFERENCE_SEARCH_VECTOR = SearchVector(
    "abstract", "title", "authors", "authors_short", "year", "journal", config="english"
)
