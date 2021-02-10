from typing import List

from docx.document import Document
from docx.shared import Inches

from .base import BaseCell, BaseTable
from .parser import QuillParser


class GenericCell(BaseCell):
    quill_text: str = "<p></p>"

    def to_docx(self, block):
        parser = QuillParser()
        return parser.feed(self.quill_text, block)


class GenericTable(BaseTable):
    column_widths: List[int] = []
    cells: List[GenericCell]

    def to_docx(self, docx: Document = None):
        docx = super().to_docx(docx)
        table = docx.tables[0]

        if len(self.column_widths):
            # Column width should be set on a per cell basis
            # https://github.com/python-openxml/python-docx/issues/360#issuecomment-277385644
            for i, width in enumerate(self.column_widths[: self.rows]):
                for cell in table.columns[i].cells:
                    cell.width = Inches(width)

        return docx

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
