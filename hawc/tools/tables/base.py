from typing import List

from docx import Document
from pydantic import BaseModel, conint


class BaseCell(BaseModel):
    header: bool = False
    row: conint(ge=0)
    column: conint(ge=0)
    row_span: conint(ge=1) = 1
    col_span: conint(ge=1) = 1

    def __str__(self):
        return f"Cell (row={self.row}, column={self.column})"

    def row_order_index(self, columns):
        return self.row * columns + self.column

    def to_dict(self):
        return {
            "row": self.row,
            "column": self.column,
            "row_span": self.row_span,
            "col_span": self.col_span,
            "html": self.to_html(),
        }

    def to_docx(self, block):
        raise NotImplementedError("Need 'to_docx' method on cell")

    def to_html(self):
        raise NotImplementedError("Need 'to_html' method on cell")


class BaseTable(BaseModel):
    rows: conint(gt=0)
    columns: conint(gt=0)
    _cells: List[BaseCell] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_cells()
        self._cells.sort(key=lambda cell: cell.row_order_index(self.columns))
        self._validate_cells()

    def _validate_cells(self):
        cells = self._cells
        table_cells = [[False] * self.columns for _ in range(self.rows)]
        for cell in cells:
            try:
                for i in range(cell.row_span):
                    for j in range(cell.col_span):
                        if table_cells[cell.row + i][cell.column + j]:
                            raise ValueError(f"Cell overlap at {cell}")
                        table_cells[cell.row + i][cell.column + j] = True
            except IndexError:
                raise ValueError(f"{cell} outside of table bounds")

    def _add_cells(self):
        raise NotImplementedError("Need '_add_cells' method on table")

    def get_cells(self):
        return [cell.to_dict() for cell in self._cells]

    def to_docx(self, docx: Document = None):
        if docx is None:
            docx = Document()
        table = docx.add_table(rows=self.rows, cols=self.columns)
        table.style = "Table Grid"
        for cell in self._cells:
            table_cell = table.cell(cell.row, cell.column)
            span_cell = table.cell(cell.row + cell.row_span - 1, cell.column + cell.col_span - 1)
            table_cell.merge(span_cell)
            # Remove default paragraph
            paragraph = table_cell.paragraphs[0]._element
            paragraph.getparent().remove(paragraph)
            cell.to_docx(table_cell)
        return docx

    @classmethod
    def build_default(cls):
        raise NotImplementedError("Need 'build_default' method on table")

    class Config:
        underscore_attrs_are_private = True
