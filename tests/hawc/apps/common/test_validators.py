import pytest
from django.core.exceptions import ValidationError
from pydantic import BaseModel

from hawc.apps.common.validators import (
    NumericTextValidator,
    validate_exact_ids,
    validate_html_tags,
    validate_hyperlinks,
    validate_json_pydantic,
)


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
        '<a href="https://hawcproject.org">Valid</a>',
        '<a href="http://epa.gov">Valid</a>',
        '<a href="/local-path/#test?foo=T&bar=F">Valid</a>',
    ]:
        assert validate_hyperlinks(text) == text

    # these are invalid
    for text in [
        '<a href="https://google.com">Invalid</a>',  # invalid domain
        '<a href="https://facebook.com">Invalid</a>',  # invalid domain
        '<a href="https://wikipedia.org">Invalid</a>',  # invalid domain
        '<a href="https://epa.gov">Valid</a> and <a href="https://google.com">Invalid</a>',  # invalid domain
        '<a href="/local-path">Invalid</a>',  # missing trailing slash
        '<a href="/local-path.png">Invalid</a>',  # filename extension; missing trailing slash
        '<a href="/local-path.png/">Invalid</a>',  # filename extension
    ]:
        with pytest.raises(ValidationError, match="Invalid hyperlinks"):
            validate_hyperlinks(text)


def test_validate_exact_ids():
    # success cases
    assert validate_exact_ids([1, 2], [1, 2], "foo") is None
    assert validate_exact_ids([1, 2], [2, 1], "foo") is None

    # failure cases
    with pytest.raises(ValidationError, match=r"Missing ID\(s\) in foo: 1"):
        validate_exact_ids([1, 2], [2], "foo")
    with pytest.raises(ValidationError, match=r"Extra ID\(s\) in foo: 3"):
        validate_exact_ids([1, 2], [1, 2, 3], "foo")


def test_numeric_text_validator():
    validator = NumericTextValidator()
    for value in ["1", "-3.2E-7", "< 1e-4", "<3", "> 4", "< LOD", "<LOQ"]:
        assert validator(value) is None

    for value in ["non-numeric", "< 3.2 LOD", "<", "<<2", "1 2", "e-4"]:
        with pytest.raises(ValidationError, match="Must be number-like"):
            validator(value)


class PersonSchema(BaseModel):
    name: str
    age: int


def test_validate_json_pydantic():
    validator = validate_json_pydantic(PersonSchema)
    # invalid
    for data in ["", "not JSON", "[]", "{}", '{"name": "johnny"}']:
        with pytest.raises(ValidationError):
            validator(data)
    # valid
    assert validator('{"name": "johnny", "age": 30}') is None
