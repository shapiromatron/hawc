import pytest
from django.core.exceptions import ValidationError

from hawc.apps.common.forms import ConfirmationField, QuillField


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
            ("<script>alert();</script>", ""),
            # remove attribute
            (
                '<a href="www.example.com" title="title">link</a>',
                '<a href="www.example.com" rel="noopener noreferrer">link</a>',
            ),
            # remove some styles
            (
                '<span style="color:blue;display:none">test</span>',
                '<span style="color:blue;">test</span>',
            ),
        ]
        for input_html, output_html in data:
            assert fld.to_python(input_html) == output_html


class TestConfirmationField:
    def test_validate(self):
        fld = ConfirmationField()

        # valid
        fld.validate("confirm")

        # invalid
        for value in [" ", "confirm!", " confirm "]:
            with pytest.raises(ValidationError):
                fld.validate(value)

    def test_check_value(self):
        # confirm that changing check value works
        fld = ConfirmationField(check_value="test")
        fld.validate("test")
        with pytest.raises(ValidationError):
            fld.validate("confirm")
