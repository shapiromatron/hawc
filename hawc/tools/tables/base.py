from typing import List

from docx import Document as create_document
from docx.document import Document
from pydantic import BaseModel, conint


class BaseCell(BaseModel):
    header: bool = False
    row: conint(ge=0) = 0
    column: conint(ge=0) = 0
    row_span: conint(ge=1) = 1
    col_span: conint(ge=1) = 1

    def __str__(self):
        return f"{self.__class__.__name__} (row={self.row}, column={self.column})"

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

    @classmethod
    def parse_args(cls, *args):
        return cls(**{key: arg for key, arg in zip(cls.__fields__.keys(), args)})


class BaseCellGroup(BaseModel):
    cells: List[BaseCell] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_cells()

    def add_offset(self, row=0, column=0):
        for cell in self.cells:
            cell.row += row
            cell.column += column

    @property
    def rows(self):
        if len(self.cells) == 0:
            return 0
        return max(cell.row + cell.row_span for cell in self.cells)

    @property
    def columns(self):
        if len(self.cells) == 0:
            return 0
        return max(cell.column + cell.col_span for cell in self.cells)

    def _set_cells(self):
        pass


class BaseTable(BaseCellGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_cells(self.cells)
        self.sort_cells()

    def validate_cells(self, cells):
        if len(cells) < 1:
            raise ValueError("At least one cell is required.")

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

    def sort_cells(self):
        self.cells.sort(key=lambda cell: cell.row_order_index(self.columns))

    def to_docx(self, docx: Document = None):
        if docx is None:
            docx = create_document()
        table = docx.add_table(rows=self.rows, cols=self.columns)
        table.style = "Table Grid"
        for cell in self.cells:
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
        raise NotImplementedError("Need 'build_default' method")
