from typing import List

from .base import BaseCell, BaseTable
from .parser import QuillParser


class GenericCell(BaseCell):
    quill_text: str

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.quill_text, block)

    def to_html(self):
        return self.quill_text


class GenericTable(BaseTable):
    cells: List[GenericCell]

    def _add_cells(self):
        self._cells.clear()
        self._cells.extend(self.cells)

    @classmethod
    def build_default(cls):
        return cls.parse_raw(
            """
        {
            "rows": 2,
            "columns": 2,
            "cells": [
                {
                    "header": true,
                    "row": 0,
                    "column": 0,
                    "quill_text": "<p>A</p>"
                },
                {
                    "header": true,
                    "row": 0,
                    "column": 1,
                    "quill_text": "<p>B</p>"
                },
                {
                    "header": false,
                    "row": 1,
                    "column": 0,
                    "quill_text": "<p>C</p>"
                },
                {
                    "header": false,
                    "row": 1,
                    "column": 1,
                    "quill_text": "<p>D</p>"
                }
            ]
        }
        """
        )
