import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import DataTableWrapper from "shared/components/DataTableWrapper";

import TableCell from "./TableCell";
import TableCellEdit from "./TableCellEdit";

@observer
class Table extends Component {
    render() {
        const {store, forceReadOnly} = this.props,
            {editMode} = store,
            {interactive} = store.settings,
            useDt = interactive && !(editMode && !forceReadOnly);
        return useDt ? (
            <DataTableWrapper>{this.renderTable()}</DataTableWrapper>
        ) : (
            this.renderTable()
        );
    }
    renderTable() {
        const {store, forceReadOnly} = this.props,
            {bodyRowIndexes, headerRowIndexes, cellsByRow} = store,
            editMode = store.editMode && !forceReadOnly,
            Cell = editMode ? TableCellEdit : TableCell;
        return (
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
                                {cellsByRow[rowIndex].map(cell => (
                                    <Cell key={cell.column} store={store} cell={cell} />
                                ))}
                            </tr>
                        );
                    })}
                </thead>
                <tbody>
                    {bodyRowIndexes.map(rowIndex => {
                        return (
                            <tr key={rowIndex}>
                                {cellsByRow[rowIndex].map(cell => (
                                    <Cell key={cell.column} store={store} cell={cell} />
                                ))}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    }
}

Table.defaultProps = {
    forceReadOnly: false,
};

Table.propTypes = {
    store: PropTypes.object.isRequired,
    forceReadOnly: PropTypes.bool,
};

export default Table;
