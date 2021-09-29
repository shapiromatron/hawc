import re

EXTERNAL_LINK = 0
PUBMED = 1
HERO = 2
RIS = 3
DOI = 4
WOS = 5
SCOPUS = 6
EMBASE = 7
REFERENCE_DATABASES = (
    (PUBMED, "PubMed"),
    (HERO, "HERO"),
    (RIS, "RIS (EndNote/Reference Manager)"),
    (DOI, "DOI"),
    (WOS, "Web of Science"),
    (SCOPUS, "Scopus"),
    (EMBASE, "Embase"),
)


# generalized/adapted from https://www.crossref.org/blog/dois-and-matching-regular-expressions/
DOI_EXACT = re.compile(r"^10.\d{4,9}/[^\s]+$")
DOI_EXAMPLE = "10.1234/s123456"
