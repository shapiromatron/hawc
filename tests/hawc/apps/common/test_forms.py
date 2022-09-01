import pytest
from django.core.exceptions import ValidationError

from hawc.apps.common.forms import QuillField


class TestQuillField:
    def test_validate(self):
        fld = QuillField()

        # valid
        html = '<a href="http://www.example.gov">link</a>'
        fld.validate(html)

        # invalid
        for html in [
            '<a href="ftp://www.example.gov">link</a>',  # schema
            '<a href="http://www.example.com">link</a>',  # tld
        ]:
            with pytest.raises(ValidationError):
                fld.validate(html)

    def test_to_python(self):
        fld = QuillField()
        data = [
            # remove script tag
            ("<script>alert();</script>", "alert();"),
            # remove attribute
            (
                '<a href="www.example.com" title="title">link</a>',
                '<a href="www.example.com">link</a>',
            ),
            # remove some styles
            (
                '<span style="color:blue;display:none">test</span>',
                '<span style="color:blue;">test</span>',
            ),
        ]
        for input_html, output_html in data:
            assert fld.to_python(input_html) == output_html
