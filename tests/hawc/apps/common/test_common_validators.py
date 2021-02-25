import pytest
from django.core.exceptions import ValidationError

from hawc.apps.common.validators import validate_html_tags


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
