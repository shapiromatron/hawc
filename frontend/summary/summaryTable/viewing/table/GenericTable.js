import {inject, observer} from "mobx-react";
import {toJS} from "mobx";
import React, {Component} from "react";
import PropTypes from "prop-types";

@inject("store")
@observer
class GenericTable extends Component {
    renderCells() {
        return;
    }
    renderRows() {
        const {table, rowOrderEnums, CELL_ENUM} = this.props.store,
            {content} = toJS(table),
            table_cells = toJS(this.props.store.cells);
        let rows = [],
            cellIndex = 0;
        for (let r = 0; r < content.rows; r++) {
            let cells = [];
            for (let c = 0; c < content.columns; c++) {
                let index = r * content.rows + c,
                    cellEnum = rowOrderEnums[index];
                if (cellEnum == CELL_ENUM.CELL) {
                    let cell = table_cells[cellIndex];
                    cells.push(
                        <td
                            rowSpan={cell.row_span}
                            colSpan={cell.col_span}
                            dangerouslySetInnerHTML={{__html: cell.html}}></td>
                    );
                    cellIndex++;
                } else if (cellEnum == CELL_ENUM.EMPTY) {
                    cells.push(<td></td>);
                }
            }
            rows.push(<tr>{cells}</tr>);
        }
        return rows;
    }
    render() {
        return (
            <>
                <table className="table table-bordered">{this.renderRows()}</table>
            </>
        );
    }
}

GenericTable.propTypes = {
    store: PropTypes.object,
};

export default GenericTable;
