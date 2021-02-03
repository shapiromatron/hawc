import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import CellModal from "./CellModal";

@observer
class TableCell extends Component {
    render() {
        const {cell, store} = this.props,
            elType = cell.header ? "th" : "td";

        // instead of using jsx; create manually
        return React.createElement(
            elType,
            {
                rowSpan: cell.row_span,
                colSpan: cell.col_span,
            },
            [
                <button
                    className="float-right btn btn-light btn-sm"
                    key={0}
                    onClick={() => {
                        store.editSelectedCell(cell.row, cell.column);
                    }}>
                    <i className="fa fa-edit"></i>&nbsp;Edit
                </button>,
                <div key={1} dangerouslySetInnerHTML={{__html: cell.quill_text}}></div>,
            ]
        );
    }
}
TableCell.propTypes = {
    store: PropTypes.object.isRequired,
    cell: PropTypes.object.isRequired,
};

@observer
class TableForm extends Component {
    render() {
        const {store} = this.props,
            {bodyRowIndexes, headerRowIndexes, cellsByRow} = store;

        return (
            <>
                <button className="btn btn-primary float-right mb-1" onClick={store.addColumn}>
                    <i className="fa fa-plus"></i>Add column
                </button>
                <table className="table table-striped table-sm">
                    <thead>
                        {headerRowIndexes.map(rowIndex => {
                            return (
                                <tr key={rowIndex}>
                                    {cellsByRow[rowIndex].map(cell => {
                                        return (
                                            <TableCell
                                                key={cell.column}
                                                store={store}
                                                cell={cell}
                                            />
                                        );
                                    })}
                                </tr>
                            );
                        })}
                    </thead>
                    <tbody>
                        {bodyRowIndexes.map(rowIndex => {
                            return (
                                <tr key={rowIndex}>
                                    {cellsByRow[rowIndex].map(cell => {
                                        return (
                                            <TableCell
                                                key={cell.column}
                                                store={store}
                                                cell={cell}
                                            />
                                        );
                                    })}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
                <button className="btn btn-primary" onClick={store.addRow}>
                    <i className="fa fa-plus"></i>Add row
                </button>
                <CellModal store={store} />
            </>
        );
    }
}

TableForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default TableForm;
