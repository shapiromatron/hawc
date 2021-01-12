from enum import IntEnum
from typing import List

from docx import Document
from pydantic import BaseModel, conint, validator

from .parser import CellHTMLParser


class CellEnum(IntEnum):
    CELL = 1
    EMPTY = 2
    SKIP = 3


class GenericTableCell(BaseModel):
    header: bool = False
    row: conint(ge=0)
    column: conint(ge=0)
    row_span: conint(ge=1) = 1
    col_span: conint(ge=1) = 1
    html_text: str

    def __str__(self):
        return "CELL STRING"

    def row_order_index(self, rows):
        return (self.column) * rows + self.row

    def to_docx(self, par):
        parser = CellHTMLParser()
        return parser.feed(self.html_text, par)


class GenericTable(BaseModel):
    rows: conint(gt=0)
    columns: conint(gt=0)
    cells: List[GenericTableCell]

    @validator("cells")
    def validate_cells(cls, cells, values):
        table_cells = [[False] * values["columns"] for _ in range(values["rows"])]
        for cell in cells:
            try:
                for i in range(cell.row_span):
                    for j in range(cell.col_span):
                        if table_cells[cell.row + i][cell.column + j]:
                            raise ValueError("Cell overlap")
                        table_cells[cell.row + i][cell.column + j] = True
            except IndexError:
                raise ValueError("Cell outside of table bounds")
        return cells.sort(key=lambda cell: cell.row_order_index(values["rows"]))

    def row_order_enums(self):
        enums = [CellEnum.EMPTY] * (self.columns * self.rows)
        for cell in self.cells:
            cell_index = cell.row_order_index(self.rows)
            enums[cell_index] = CellEnum.CELL
            for i in range(1, cell.row_span):
                for j in range(1, cell.col_span):
                    index = cell_index + i + (j * self.rows)
                    enums[index] = CellEnum.SKIP

    def to_docx(self, docx: Document = None):
        if docx is None:
            docx = Document()
        table = docx.add_table(rows=self.rows, cols=self.columns)
        for cell in self.cells:
            table_cell = table.cell(cell.row, cell.column)
            cell_par = table_cell.add_paragraph()
            cell.to_docx(cell_par)
        return docx
