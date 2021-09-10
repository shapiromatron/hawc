from pathlib import Path

from docx import Document

from hawc.tools.tables.parser import QuillParser

from . import documents_equal

DATA_PATH = Path(__file__).parent.absolute() / "data"


class TestQuillParser:
    def test_parser(self, quill_html):
        document = Document()
        parser = QuillParser()
        parser.feed(quill_html, document._body)
        saved_document = Document(DATA_PATH / "parsed_html.docx")

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
