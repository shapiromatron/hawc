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
    def build_default(cls):
        return cls.parse_raw(
            """
        {
            "column_widths": [10, 10],
            "cells": [
                {
                    "header": true,
                    "row": 0,
                    "column": 0,
                    "quill_text": "<p>A1</p>"
                },
                {
                    "header": true,
                    "row": 0,
                    "column": 1,
                    "quill_text": "<p>B1</p>"
                },
                {
                    "header": false,
                    "row": 1,
                    "column": 0,
                    "quill_text": "<p>A2</p>"
                },
                {
                    "header": false,
                    "row": 1,
                    "column": 1,
                    "quill_text": "<p>B2</p>"
                }
            ]
        }
        """
        )
