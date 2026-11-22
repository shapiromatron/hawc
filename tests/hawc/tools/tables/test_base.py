import pytest
from docx import Document

from hawc.tools.tables.base import BaseCell, BaseCellGroup, BaseTable, to_landscape
from hawc.tools.tables.generic import GenericCell


class HtmlCell(BaseCell):
    def to_html(self):
        return "<p>html</p>"


def test_to_landscape():
    document = Document()
    to_landscape(document)
    section = document.sections[0]
    assert section.page_width > section.page_height


class TestBaseCell:
    def test_str(self):
        assert str(BaseCell(row=1, column=2)) == "BaseCell (row=1, column=2)"

    def test_row_order_index(self):
        assert BaseCell(row=2, column=1).row_order_index(3) == 7

    def test_to_dict(self):
        assert HtmlCell(row=1, row_span=2).to_dict() == {
            "row": 1,
            "column": 0,
            "row_span": 2,
            "col_span": 1,
            "html": "<p>html</p>",
        }

    def test_to_docx(self):
        with pytest.raises(NotImplementedError):
            BaseCell().to_docx(None, None)

    def test_parse_args(self):
        cell = GenericCell.parse_args(True, 1, 2, 3, 4, "<p>a</p>")
        assert (cell.header, cell.row, cell.column, cell.row_span, cell.col_span) == (
            True,
            1,
            2,
            3,
            4,
        )
        with pytest.raises(ValueError, match="argument"):
            GenericCell.parse_args(True)


class TestBaseCellGroup:
    def test_add_offset(self):
        group = BaseCellGroup(cells=[BaseCell(row=0, column=0)])
        group.add_offset(row=1, column=2)
        assert (group.cells[0].row, group.cells[0].column) == (1, 2)

    def test_rows_columns(self):
        assert (BaseCellGroup().rows, BaseCellGroup().columns) == (0, 0)
        group = BaseCellGroup(cells=[BaseCell(row=1, column=2, row_span=2, col_span=3)])
        assert (group.rows, group.columns) == (3, 5)


class TestBaseTable:
    def test_validate_cells(self):
        with pytest.raises(ValueError, match="Cell overlap"):
            BaseTable(cells=[BaseCell(col_span=2), BaseCell(column=1)])
        table = BaseTable(cells=[BaseCell(row_span=2)])
        with pytest.raises(ValueError, match="outside of table bounds"):
            table.validate_cells([BaseCell(row=5)])

    def test_sort_cells(self):
        table = BaseTable(cells=[BaseCell(row=1), BaseCell(column=1), BaseCell(column=2)])
        assert [c.row_order_index(table.columns) for c in table.cells] == [1, 2, 3]

    def test_get_data(self):
        assert BaseTable.get_data(1) == {}

    def test_get_default_props(self):
        with pytest.raises(NotImplementedError):
            BaseTable.get_default_props()
        with pytest.raises(NotImplementedError):
            BaseTable.build_default()
