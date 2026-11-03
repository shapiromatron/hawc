from hawc.apps.lit.constants import DOI_EXACT, ReferenceDatabase


def test_doi_regex():
    # valid
    assert DOI_EXACT.fullmatch("10.1234/1234") is not None
    assert DOI_EXACT.fullmatch("10.1234/fff") is not None
    assert DOI_EXACT.fullmatch("10.1234/fff-1234/-._;()") is not None

    # invalid
    assert DOI_EXACT.fullmatch(" 10.1234/fff") is None
    assert DOI_EXACT.fullmatch("10.1234/fff ") is None
    assert DOI_EXACT.fullmatch("10.abcd") is None
    assert DOI_EXACT.fullmatch("10.abcd/") is None
    assert DOI_EXACT.fullmatch("10.abcd/fff") is None
    assert DOI_EXACT.fullmatch("doi:10.1234/fff") is None


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
