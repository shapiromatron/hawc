import _ from "lodash";
import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

import {getCellExcelName} from "./common";
import ColWidthTable from "./ColWidthTable";
import {QuickEditCell, EditCellModal} from "./EditCell";

@observer
class TableCell extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isHovering: false,
        };
    }
    render() {
        const {cell, store} = this.props,
            {quickEditCell} = store,
            isQuickEditCell = quickEditCell === cell,
            elType = cell.header ? "th" : "td",
            {isHovering} = this.state;

        // instead of using jsx; create manually
        return React.createElement(
            elType,
            {
                rowSpan: cell.row_span,
                colSpan: cell.col_span,
                onClick: e => {
                    if (
                        !e.target.classList.contains("btn") &&
                        !e.target.classList.contains("fa-edit")
                    ) {
                        store.selectCellEdit(cell, true);
                    }
                },
                onMouseEnter: () => this.setState({isHovering: true}),
                onMouseLeave: () => this.setState({isHovering: false}),
            },
            [
                <button
                    className="float-right btn btn-light btn-sm"
                    style={{opacity: isHovering && !isQuickEditCell ? 1 : 0}}
                    key={0}
                    onClick={() => {
                        store.selectCellEdit(cell, false);
                    }}>
                    <i className="fa fa-edit mr-1"></i>Edit {getCellExcelName(cell)}
                </button>,
                isQuickEditCell ? (
                    <QuickEditCell key={1} store={store} />
                ) : (
                    <div key={1} dangerouslySetInnerHTML={{__html: cell.quill_text}}></div>
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
                <div className="bg-info p-2 clearfix">
                    <button className="btn btn-light mx-1" onClick={store.toggleShowColumnEdit}>
                        <i className="fa fa-arrows-h mr-1"></i>Column width
                    </button>
                    <div className="float-right">
                        <button className="btn btn-light mx-1" onClick={store.addColumn}>
                            <i className="fa fa-plus mr-1"></i>Add column
                        </button>
                        <button className="btn btn-light mx-1" onClick={store.addRow}>
                            <i className="fa fa-plus mr-1"></i>Add row
                        </button>
                    </div>
                </div>
                {store.showColumnEdit ? <ColWidthTable store={store} /> : null}
                <h4>Editing table</h4>
                <p className="text-muted">
                    Click any cell to edit the text, or press the edit button on a cell to modify
                    the table structure (eg., merging rows and columns).
                </p>
                <table className="summaryTable table table-bordered table-sm">
                    <colgroup>
                        {_.map(store.colWidthStyle, (style, i) => {
                            return <col key={i} style={style} />;
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
                <EditCellModal store={store} />
            </>
        );
    }
}

TableForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default TableForm;
