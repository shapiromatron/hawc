import {observer} from "mobx-react";
import {toJS} from "mobx";
import React, {Component} from "react";
import PropTypes from "prop-types";

const CELL_ENUM = {
        CELL: 1,
        EMPTY: 2,
        SKIP: 3,
    },
    getRowOrderEnums = function(content) {
        const {rows, columns, cells} = content;
        let enums = Array(rows * columns).fill(CELL_ENUM.EMPTY);
        for (let cell of cells) {
            let cellIndex = cell.row * columns + cell.column;
            for (let r = 0; r < cell.row_span; r++) {
                for (let c = 0; c < cell.col_span; c++) {
                    let index = cellIndex + c + r * columns;
                    enums[index] = CELL_ENUM.SKIP;
                }
            }
            enums[cellIndex] = CELL_ENUM.CELL;
        }
        return enums;
    };

@observer
class Table extends Component {
    renderCells() {
        return;
    }
    renderRows() {
        const settings = toJS(this.props.settings),
            rowOrderEnums = getRowOrderEnums(settings);
        let rows = [],
            cellIndex = 0;

        for (let r = 0; r < settings.rows; r++) {
            let cells = [];
            for (let c = 0; c < settings.columns; c++) {
                let index = r * settings.rows + c,
                    cellEnum = rowOrderEnums[index];
                if (cellEnum == CELL_ENUM.CELL) {
                    let cell = settings.cells[cellIndex];
                    cells.push(
                        <td
                            key={c}
                            rowSpan={cell.row_span}
                            colSpan={cell.col_span}
                            dangerouslySetInnerHTML={{__html: cell.quill_text}}></td>
                    );
                    cellIndex++;
                } else if (cellEnum == CELL_ENUM.EMPTY) {
                    cells.push(<td key={c}></td>);
                }
            }
            rows.push(<tr key={r}>{cells}</tr>);
        }
        return rows;
    }
    render() {
        return (
            <table className="table table-bordered">
                <tbody>{this.renderRows()}</tbody>
            </table>
        );
    }
}

Table.propTypes = {
    settings: PropTypes.object.isRequired,
};

export default Table;
