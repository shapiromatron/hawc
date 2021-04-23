import pytest
from django.core.exceptions import ValidationError

from hawc.apps.common.validators import validate_html_tags, validate_hyperlinks


def test_validate_html_tags():
    # these are valid
    for text in [
        "",
        "<ul><li>Hi</li></ul>",
        "<ol><li>Hi</li></ol>",
        "<p>Hi</p>",
        '<a href="/">Hi</a>',
        "<p><strong><em>Hi</em></strong></p>",
    ]:
        assert validate_html_tags(text) == text

    # these are invalid
    for text in [
        "<div></div>",
        "<script></script>",
        "<style></style>",
    ]:
        with pytest.raises(ValidationError, match="Invalid html tags"):
            validate_html_tags(text)


def test_validate_hyperlinks():
    # these are valid
    for text in [
        "",
        "No hyperlinks href",
        "Not an anchor https://invalid.com",
        '<a href="https://epa.gov">Valid</a>',
        '<a href="https://pubmed.ncbi.nlm.nih.gov/123123/">Valid</a>',
        '<a href="https://iarc.who.int/">Valid</a>',
        '<a href="https://www.unc.edu/">Valid</a>',
        '<a href="https://oehha.ca.gov/">Valid</a>',
        '<a href="http://epa.gov">Valid</a>',
        '<a href="/local-path#test?foo=T&bar=F">Valid</a>',
    ]:
        assert validate_hyperlinks(text) == text

    # these are invalid
    for text in [
        '<a href="https://google.com">Invalid</a>',
        '<a href="https://facebook.com">Invalid</a>',
        '<a href="https://wikipedia.org">Invalid</a>',
        '<a href="https://epa.gov">Valid</a> and <a href="https://google.com">Invalid</a>',
    ]:
        with pytest.raises(ValidationError, match="Invalid hyperlinks"):
            validate_hyperlinks(text)
