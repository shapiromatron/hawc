import pytest

from hawc.apps.lit.constants import DOI_EXACT, ReferenceDatabase


@pytest.mark.parametrize(
    ("doi", "valid"),
    [
        ("10.1234/1234", True),
        ("10.1234/fff", True),
        ("10.1234/fff-1234/-._;()", True),
        (" 10.1234/fff", False),
        ("10.1234/fff ", False),
        ("10.abcd", False),
        ("10.abcd/", False),
        ("10.abcd/fff", False),
        ("doi:10.1234/fff", False),
    ],
)
def test_doi_exact(doi, valid):
    assert (DOI_EXACT.fullmatch(doi) is not None) is valid


class TestReferenceDatabase:
    def test_export_map(self):
        assert ReferenceDatabase.export_map() == {
            0: "Manually added",
            1: "PubMed ID",
            2: "HERO ID",
            3: "RIS (EndNote/Reference Manager)",
            4: "DOI",
            5: "Web of Science ID",
            6: "Scopus ID",
            7: "Embase ID",
        }
