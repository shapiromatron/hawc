import h from "shared/utils/helpers";

export const getCellExcelName = function (cell) {
    const topLeft = `${h.excelCoords(cell.row, cell.column)}`;

    return cell.row_span == 1 && cell.col_span == 1
        ? topLeft
        : `${topLeft}:${h.excelCoords(
              cell.row + cell.row_span - 1,
              cell.column + cell.col_span - 1
          )}`;
};
