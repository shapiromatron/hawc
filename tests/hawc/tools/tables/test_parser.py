from pathlib import Path

import pytest
from docx import Document

from hawc.tools.tables.parser import (
    QuillParser,
    color_background,
    has_inner_text,
    ol_wrapper,
    strip_enclosing_tag,
    strip_tags,
    tag_wrapper,
    ul_wrapper,
)

from . import documents_equal

FILE_PATH = Path(__file__).parent.absolute() / "data" / "parsed_html.docx"


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (("a", "p"), "<p>a</p>"),
        (("a", "p", "strong", "em"), "<p><strong><em>a</em></strong></p>"),
    ],
)
def test_tag_wrapper(args, expected):
    assert tag_wrapper(*args) == expected


def test_strip_tags():
    assert strip_tags("<p>a <strong>b</strong></p>") == "a b"


@pytest.mark.parametrize(
    ("text", "expected"),
    [("<p>a</p>", "a"), ("<p>a</p><p>b</p>", "a</p><p>b"), ("a", "a"), ("<p>a", "<p>a")],
)
def test_strip_enclosing_tag(text, expected):
    assert strip_enclosing_tag(text, "p") == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [("<p>a</p>", True), ("<p> </p>", False), ("", False)],
)
def test_has_inner_text(text, expected):
    assert has_inner_text(text) is expected


def test_ul_wrapper():
    assert ul_wrapper(["a", "b"]) == "<ul><li>a</li><li>b</li></ul>"


def test_ol_wrapper():
    assert ol_wrapper(["a", "b"]) == "<ol><li>a</li><li>b</li></ol>"


def test_color_background():
    cell = Document().add_table(rows=1, cols=1).cell(0, 0)
    color_background(cell, "#4B9CD3")
    assert cell._element.xpath("//w:shd/@w:fill") == ["4B9CD3"]


class TestQuillParser:
    def test_parser(self, rewrite_data_files: bool, quill_html):
        document = Document()
        parser = QuillParser()
        parser.feed(quill_html, document._body)
        if rewrite_data_files:
            document.save(FILE_PATH)
        saved_document = Document(FILE_PATH)

        assert documents_equal(document, saved_document)

    def test_parse_url(self):
        # no base url
        parser = QuillParser()
        assert parser.parse_url("/test/") == "/test/"
        assert parser.parse_url("https://def.com/test/") == "https://def.com/test/"

        # base url
        parser = QuillParser(base_url="https://abc.com")
        assert parser.parse_url("/test/") == "https://abc.com/test/"
        assert parser.parse_url("https://def.com/test/") == "https://def.com/test/"
