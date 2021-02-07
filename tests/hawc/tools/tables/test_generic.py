from pathlib import Path

import pytest
from docx import Document
from pydantic import ValidationError as PydanticError

from hawc.tools.tables.generic import GenericTable

from . import documents_equal

DATA_PATH = Path(__file__).parent.absolute() / "data"


class TestGenericTable:
    def test_docx(self, quill_html):
        document = Document()
        obj = {
            "rows": 4,
            "columns": 4,
            "cells": [
                {"row": 0, "column": 0, "col_span": 2, "row_span": 2, "quill_text": quill_html},
                {"row": 2, "column": 2, "col_span": 2, "row_span": 2, "quill_text": quill_html},
            ],
        }
        table = GenericTable.parse_obj(obj)
        document = table.to_docx()
        saved_document = Document(DATA_PATH / "generic_report.docx")

        assert documents_equal(document, saved_document)

    def test_good_parse(self):
        # all table properties are present and valid
        obj = {
            "rows": 1,
            "columns": 1,
            "cells": [],
        }
        GenericTable.parse_obj(obj)

        # all cell properties are present and valid
        obj = {
            "rows": 1,
            "columns": 1,
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
        # missing rows
        with pytest.raises(PydanticError):
            obj = {
                "columns": 1,
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

        # missing columns
        with pytest.raises(PydanticError):
            obj = {
                "rows": 1,
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

        # cells out of bounds
        with pytest.raises(PydanticError, match="outside of table bounds"):
            obj = {
                "rows": 1,
                "columns": 1,
                "cells": [
                    {
                        "row": 0,
                        "column": 0,
                        "col_span": 2,
                        "row_span": 1,
                        "quill_text": "<p>paragraph</p>",
                    },
                ],
            }
            GenericTable.parse_obj(obj)

        # cells overlap
        with pytest.raises(PydanticError, match="Cell overlap"):
            obj = {
                "rows": 1,
                "columns": 2,
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
            GenericTable.parse_obj(obj)
