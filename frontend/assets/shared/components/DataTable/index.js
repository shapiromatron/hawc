import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";
import Tablesort from "tablesort";

import h from "shared/utils/helpers";
import "./sorts";

class DataTable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            tableId: h.randomString(),
        };
    }
    componentDidMount() {
        setTimeout(() => {
            const table = document.getElementById(this.state.tableId);
            new Tablesort(table);
        }, 1000);
    }
    render() {
        const rows = this.props.dataset,
            {tableId} = this.state,
            columns = _.map(rows[0], (val, key) => key),
            renderers = this.props.renderers || {};

        return (
            <table id={tableId} className="table table-striped table-condensed">
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
}
DataTable.propTypes = {
    dataset: PropTypes.array.isRequired,
    renderers: PropTypes.object,
};

export default DataTable;
