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
