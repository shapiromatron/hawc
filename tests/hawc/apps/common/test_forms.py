import pytest
from django.core.exceptions import ValidationError

from hawc.apps.common.forms import QuillField


class TestQuillField:
    def test_validate(self):
        fld = QuillField()

        # invalid scheme
        html = '<a href="ftp://www.example.gov">link</a>'
        with pytest.raises(ValidationError):
            fld.validate(html)

        # invalid TLD
        html = '<a href="http://www.example.com">link</a>'
        with pytest.raises(ValidationError):
            fld.validate(html)

        # valid
        html = '<a href="http://www.example.gov">link</a>'
        fld.validate(html)

    def test_to_python(self):
        fld = QuillField()

        # tags should be cleaned
        html = "<script>alert();</script>"
        cleaned_html = fld.to_python(html)
        assert cleaned_html == "alert();"

        # attrs should be cleaned
        html = '<a href="www.example.com" title="title">link</a>'
        cleaned_html = fld.to_python(html)
        assert cleaned_html == '<a href="www.example.com">link</a>'

        # styles should be cleaned
        html = '<span style="color:blue;display:none">test</span>'
        cleaned_html = fld.to_python(html)
        assert cleaned_html == '<span style="color:blue;">test</span>'
