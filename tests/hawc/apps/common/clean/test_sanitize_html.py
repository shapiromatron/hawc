"""Test HTML cleanup."""

import pytest

from hawc.apps.common.clean.sanitize_html import clean_html


class TestEscapeAbstract:
    def test_expected_html(self):
        # no changes, no elements
        text = clean_html("text without any elements")
        assert text == "text without any elements"

        # no changes, expected elements
        # <mark>
        text = clean_html('<mark class="my-class">turtles</mark>')
        assert text == '<mark class="my-class">turtles</mark>'

        # <span>
        text = clean_html('<span class="my-class">BACKGROUND: </span>')
        assert text == '<span class="my-class">BACKGROUND: </span>'

        # <br>
        text = clean_html("health-care system. <br>")
        assert text == "health-care system. <br>"

        # check < still works if spaced correctly
        for a, b in (
            ("10 < 20", "10 &lt; 20"),
            ("10 <= 20", "10 &lt;= 20"),
            ("30 > 20", "30 &gt; 20"),
            ("30 >= 20", "30 &gt;= 20"),
        ):
            assert clean_html(a) == b

    def test_unexpected_html(self):
        # <median
        text = clean_html("median versus <median metal")
        assert text == "median versus "

        # <body> elements will be broken
        text = clean_html("before <body> after </body>")
        assert text == "before  after "

        # tags that aren't real will be escaped
        text = clean_html("before <10>after</10>")
        assert text == "before &lt;10&gt;after"

    def test_css(self):
        text = clean_html(
            '<span class="test" style="'
            "position: absolute; top: 0; left: 0; width: 9999px; "
            "height: 9999px; z-index: 9999; color: blue"
            '" onmouseenter="alert(1)">This is a test!</span>'
        )
        assert text == '<span class="test" style="color: blue;">This is a test!</span>'

    def test_all(self):
        text = clean_html(
            """
        <10
        < 20
        <span></span>
        <mark></mark>
        <br/><br>
        <span class="foo"></span>
        <mark class="foo"></mark>
        """
        )
        assert (
            text
            == """
        &lt;10
        &lt; 20
        <span></span>
        <mark></mark>
        <br><br>
        <span class="foo"></span>
        <mark class="foo"></mark>
        """
        )

    @pytest.mark.parametrize(
        "html",
        [
            '<span class="smart-tag active" data-pk="1" data-type="study">Inline</span>',
            '<div class="smart-tag active" data-pk="1" data-type="study">Modal</div>',
        ],
    )
    def test_smart_tag(self, html):
        # Confirm custom smart-tag fields are properly sanitized.
        assert clean_html(html) == html
