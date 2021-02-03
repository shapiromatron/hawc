import _ from "lodash";
import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import {QuickEditCell, EditCell} from "./EditCell";

@observer
class TableCell extends Component {
    render() {
        const {cell, store} = this.props,
            {quickEditCell} = store,
            isQuickEditCell = quickEditCell === cell,
            elType = cell.header ? "th" : "td";

        // instead of using jsx; create manually
        return React.createElement(
            elType,
            {
                rowSpan: cell.row_span,
                colSpan: cell.col_span,
                onClick: e => {
                    if (
                        !isQuickEditCell &&
                        !e.target.classList.contains("btn") &&
                        !e.target.classList.contains("fa-edit")
                    ) {
                        store.selectCellEdit(cell, true);
                    }
                },
            },
            [
                <button
                    className="float-right btn btn-light btn-sm"
                    key={0}
                    onClick={() => {
                        store.selectCellEdit(cell, false);
                    }}>
                    <i className="fa fa-edit"></i>&nbsp;Edit
                </button>,
                isQuickEditCell ? (
                    <QuickEditCell key={1} store={store} />
                ) : (
                    // <div key={1} dangerouslySetInnerHTML={{__html: cell.quill_text}}></div>
                    <div key={1}>
                        [{cell.row}, {cell.column}]
                    </div>
                ),
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
                    <colgroup>
                        {_.map(store.colWidths, (w, i) => {
                            return <col key={i} style={{width: `${w}%`}}></col>;
                        })}
                    </colgroup>
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
                <EditCell store={store} />
            </>
        );
    }
}

TableForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default TableForm;
