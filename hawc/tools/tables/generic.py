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
    def build_default(cls):
        return cls.parse_raw(
            """
        {
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
