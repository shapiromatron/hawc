from pathlib import Path

from docx import Document

from hawc.tools.tables.generic import GenericTable

from . import document_compare

DATA_PATH = Path(__file__).parent.absolute() / "data"


class TestGenericTable:
    def test_docx(self, quill_html):
        document = Document()
        obj = {
            "rows": 4,
            "columns": 4,
            "cells": [
                {"row": 0, "column": 0, "col_span": 2, "row_span": 2, "html_text": quill_html},
                {"row": 2, "column": 2, "col_span": 2, "row_span": 2, "html_text": quill_html},
            ],
        }
        table = GenericTable.parse_obj(obj)
        document = table.to_docx()
        saved_document = Document(DATA_PATH / "generic_report.docx")

        document_compare(document, saved_document)
