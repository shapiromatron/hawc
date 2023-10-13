import "./sorts";

import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";
import DataTableWrapper from "shared/components/DataTableWrapper";
import h from "shared/utils/helpers";
import Tablesort from "tablesort";

class DataTable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            tableId: h.randomString(),
        };
    }
    componentDidMount() {
        const {tablesort} = this.props;
        if (tablesort) {
            setTimeout(() => {
                const table = document.getElementById(this.state.tableId);
                if (table) {
                    new Tablesort(table);
                }
            }, 1000);
        }
    }
    renderTable() {
        const rows = this.props.dataset,
            {tableId} = this.state,
            columns = _.map(rows[0], (val, key) => key),
            renderers = this.props.renderers || {};

        return (
            <table id={tableId} className="table table-striped table-sm">
                <thead>
                    <tr>
                        {columns.map((col, i) => {
                            return <th key={i}>{h.titleCase(col)}</th>;
                        })}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, i) => {
                        return (
                            <tr key={i}>
                                {columns.map((col, j) => {
                                    return (
                                        <td key={j}>
                                            {renderers[col] ? renderers[col](row) : row[col]}
                                        </td>
                                    );
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    }
    render() {
        const {datatables} = this.props;
        return datatables ? (
            <DataTableWrapper>{this.renderTable()}</DataTableWrapper>
        ) : (
            this.renderTable()
        );
    }
}
DataTable.propTypes = {
    dataset: PropTypes.array.isRequired,
    renderers: PropTypes.object,
    tablesort: PropTypes.bool,
    datatables: PropTypes.bool,
};
DataTable.defaultProps = {
    tablesort: true,
    datatables: false,
};

export default DataTable;
