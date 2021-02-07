from pathlib import Path

import pytest
from docx import Document

from hawc.tools.tables.generic import GenericTable

from . import documents_equal

DATA_PATH = Path(__file__).parent.absolute() / "data"


class TestGenericTable:
    def test_docx(self):
        document = Document()
        table = GenericTable.build_default()
        document = table.to_docx()
        saved_document = Document(DATA_PATH / "generic_report.docx")
        assert documents_equal(document, saved_document)

    def test_good_parse(self):
        # all cell properties are present and valid
        obj = {
            "cells": [
                {
                    "row": 0,
                    "column": 0,
                    "col_span": 1,
                    "row_span": 1,
                    "quill_text": "<p>paragraph</p>",
                },
            ],
        }
        GenericTable.parse_obj(obj)

    def test_bad_parse(self):
        # one cell required
        obj = {"cells": []}
        with pytest.raises(ValueError, match="At least one cell is required"):
            GenericTable.parse_obj(obj)

        # cells overlap
        obj = {
            "cells": [
                {
                    "row": 0,
                    "column": 0,
                    "col_span": 2,
                    "row_span": 1,
                    "quill_text": "<p>paragraph</p>",
                },
                {
                    "row": 0,
                    "column": 1,
                    "col_span": 1,
                    "row_span": 1,
                    "quill_text": "<p>paragraph</p>",
                },
            ],
        }
        with pytest.raises(ValueError, match="Cell overlap"):
            GenericTable.parse_obj(obj)
