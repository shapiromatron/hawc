from typing import List

from .base import BaseCell, BaseTable
from .parser import QuillParser


class GenericCell(BaseCell):
    quill_text: str = "<p></p>"

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.quill_text, block)


class GenericTable(BaseTable):
    cells: List[GenericCell]

    @classmethod
    def get_default_props(cls):
        return {
            "column_widths": [10, 10],
            "cells": [
                {
                    "header": True,
                    "row": 0,
                    "column": 0,
                    "quill_text": "<p>A1</p>",
                    "row_span": 1,
                    "col_span": 1,
                },
                {
                    "header": True,
                    "row": 0,
                    "column": 1,
                    "quill_text": "<p>B1</p>",
                    "row_span": 1,
                    "col_span": 1,
                },
                {
                    "header": False,
                    "row": 1,
                    "column": 0,
                    "quill_text": "<p>A2</p>",
                    "row_span": 1,
                    "col_span": 1,
                },
                {
                    "header": False,
                    "row": 1,
                    "column": 1,
                    "quill_text": "<p>B2</p>",
                    "row_span": 1,
                    "col_span": 1,
                },
            ],
        }
