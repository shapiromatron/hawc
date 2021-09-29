from hawc.apps.lit.constants import DOI_EXACT


def test_doi_regex():
    # valid
    assert DOI_EXACT.fullmatch("10.1234/1234") is not None
    assert DOI_EXACT.fullmatch("10.1234/fff") is not None
    assert DOI_EXACT.fullmatch("10.1234/fff-1234-._;()") is not None

    # invalid
    assert DOI_EXACT.fullmatch(" 10.1234/fff ") is None
    assert DOI_EXACT.fullmatch("10.1234/fff ") is None
    assert DOI_EXACT.fullmatch("10.abcd") is None
    assert DOI_EXACT.fullmatch("10.abcd/") is None
    assert DOI_EXACT.fullmatch("10.abcd/fff") is None
    assert DOI_EXACT.fullmatch("doi:10.1234/fff") is None
