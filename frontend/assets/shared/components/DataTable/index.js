import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";
import Tablesort from "tablesort";

import "./sorts";

class DataTable extends React.Component {
    componentDidMount() {
        setTimeout(function() {
            new Tablesort(document.getElementById("hi"));
        }, 1000);
    }
    render() {
        const rows = this.props.dataset,
            columns = _.map(rows[0], (val, key) => key),
            renderers = this.props.renderers || {};

        return (
            <table id={"hi"} className="table table-striped table-condensed">
                <thead>
                    <tr>
                        {columns.map((col, i) => {
                            return <th key={i}>{col}</th>;
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
