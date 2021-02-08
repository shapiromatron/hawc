from typing import List, Optional

from .base import BaseCell, BaseTable
from .parser import QuillParser


class GenericCell(BaseCell):
    quill_text: str = "<p></p>"

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.quill_text, block)


class GenericTable(BaseTable):
    column_widths: Optional[List[int]]
    cells: List[GenericCell]

    @classmethod
    def get_default_props(cls):
        return {
            "column_widths": [10, 10],
            "cells": [
                {"header": True, "row": 0, "column": 0, "quill_text": "<p>A1</p>"},
                {"header": True, "row": 0, "column": 1, "quill_text": "<p>B1</p>"},
                {"header": False, "row": 1, "column": 0, "quill_text": "<p>A2</p>"},
                {"header": False, "row": 1, "column": 1, "quill_text": "<p>B2</p>"},
            ],
        }
