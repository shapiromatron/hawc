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
    renderTable(data, columns) {
        const {tableId} = this.state;

        return (
            <table id={tableId} className="table table-striped table-sm">
                <thead>
                    <tr>
                        {columns.map((col, i) => {
                            return <th key={i}>{col.title}</th>;
                        })}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, i) => {
                        return (
                            <tr key={i}>
                                {columns.map((col, j) => {
                                    return <td key={j}>{row[col.data]}</td>;
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    }
    render() {
        const {dataset, renderers, datatables} = this.props,
            // apply renderers to dataset
            data = dataset.map(row =>
                _.mapValues(row, (val, key, obj) => (renderers[key] ? renderers[key](obj) : val))
            ),
            // setup columns for use in datatables
            columns = _.map(data[0], (_val, key) => ({data: key, title: h.titleCase(key)}));
        return datatables ? (
            <DataTableWrapper
                className="table table-striped table-sm"
                data={data}
                columns={columns}
            />
        ) : (
            this.renderTable(data, columns)
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
    renderers: {},
    tablesort: true,
    datatables: false,
};

export default DataTable;
