from typing import Annotated

from docx import Document as create_document
from docx.document import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Inches
from pydantic import BaseModel, Field

from .parser import QuillParser


def to_landscape(document):
    # change docx from portrait to landscape
    section = document.sections[0]
    new_width, new_height = section.page_height, section.page_width
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = new_width
    section.page_height = new_height


class BaseCell(BaseModel):
    header: bool = False
    row: Annotated[int, Field(ge=0)] = 0
    column: Annotated[int, Field(ge=0)] = 0
    row_span: Annotated[int, Field(ge=1)] = 1
    col_span: Annotated[int, Field(ge=1)] = 1

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

    def to_docx(self, parser: QuillParser, block):
        raise NotImplementedError("Need 'to_docx' method on cell")

    @classmethod
    def parse_args(cls, *args):
        return cls(**{key: arg for key, arg in zip(cls.model_fields.keys(), args, strict=True)})


class BaseCellGroup(BaseModel):
    cells: list[BaseCell] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup()
        self._set_cells()

    def _setup(self):
        # additional setup after pydantic validation goes here
        pass

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
    column_widths: list[int] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate_cells(self.cells)
        self.sort_cells()

    def validate_cells(self, cells):
        table_cells = [[False] * self.columns for _ in range(self.rows)]
        for cell in cells:
            try:
                for i in range(cell.row_span):
                    for j in range(cell.col_span):
                        if table_cells[cell.row + i][cell.column + j]:
                            raise ValueError(f"Cell overlap at {cell}")
                        table_cells[cell.row + i][cell.column + j] = True
            except IndexError as err:
                raise ValueError(f"{cell} outside of table bounds") from err

    def sort_cells(self):
        self.cells.sort(key=lambda cell: cell.row_order_index(self.columns))

    def to_docx(
        self,
        parser: QuillParser | None = None,
        docx: Document | None = None,
        landscape: bool = True,
    ):
        if parser is None:
            parser = QuillParser()
        if docx is None:
            docx = create_document()
        if landscape:
            to_landscape(docx)

        table = docx.add_table(rows=self.rows, cols=self.columns)
        table_cells = table._cells
        table.style = "Table Grid"
        columns = self.columns
        for cell in self.cells:
            cell_index = cell.row_order_index(columns)
            table_cell = table_cells[cell_index]
            span_index = cell_index + (cell.row_span - 1) * columns + cell.col_span - 1
            span_cell = table_cells[span_index]
            table_cell.merge(span_cell)
            # Remove default paragraph
            paragraph = table_cell.paragraphs[0]._element
            paragraph.getparent().remove(paragraph)
            cell.to_docx(parser, table_cell)
        if len(self.column_widths):
            # Column width should be set on a per cell basis
            # https://github.com/python-openxml/python-docx/issues/360#issuecomment-277385644
            for i, width in enumerate(self.column_widths[:columns]):
                for table_cell in table_cells[i::columns]:
                    table_cell.width = Inches(width)

        return docx

    @classmethod
    def get_data(cls, assessment_id: int, **kwargs) -> dict:
        # return any queried data needed to build the table
        return {}

    @classmethod
    def get_default_props(cls) -> dict:
        """Return the default required properties for a table.

        This should be a full set of required fields for a pydantic model, but may not include
        calculated fields which can often be inferred by the default property types.

        Returns:
            A dictionary of required property fields; often exposed in the UI.
        """
        raise NotImplementedError("Subclass implementation required")

    @classmethod
    def build_default(cls):
        return cls.model_validate(cls.get_default_props())
