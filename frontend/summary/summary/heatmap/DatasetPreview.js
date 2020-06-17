import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

class DatasetPreview extends Component {
    render() {
        const {dataset, url} = this.props;

        if (!dataset || dataset.length === 0) {
            return <div className="alert alert-danger">No data are available.</div>;
        }

        const firstRow = dataset[0],
            summary = {
                numRows: dataset.length,
                numColumns: _.keys(firstRow).length,
                columnNames: _.keys(firstRow),
            };

        return (
            <div>
                <h4>
                    Dataset overview
                    <div className="btn-group pull-right">
                        <a className="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                            Actions&nbsp;
                            <span className="caret"></span>
                        </a>
                        <ul className="dropdown-menu">
                            <li>
                                <a
                                    href={
                                        url.includes("?")
                                            ? `${url}&format=csv`
                                            : `${url}?format=csv`
                                    }>
                                    <i className="fa fa-file-text-o"></i>&nbsp;Download dataset
                                    (csv)
                                </a>
                                <a
                                    href={
                                        url.includes("?")
                                            ? `${url}&format=xlsx`
                                            : `${url}?format=xlsx`
                                    }>
                                    <i className="fa fa-file-excel-o"></i>&nbsp;Download dataset
                                    (xlsx)
                                </a>
                            </li>
                        </ul>
                    </div>
                </h4>
                <ul>
                    <li>
                        <b>Number of rows:</b>&nbsp;{summary.numRows}
                    </li>
                    <li>
                        <b>Number of columns:</b>&nbsp;{summary.numColumns}
                    </li>
                    <li>
                        <b>Columns:</b>&nbsp;{summary.columnNames.join(", ") || "<none>"}
                    </li>
                </ul>
                <h4>
                    {summary.numRows > 0
                        ? "Showing the first 10 rows ..."
                        : "No data available, select a different dataset ..."}
                </h4>
                <table className="table table-condensed table-striped">
                    <thead>
                        <tr>
                            {summary.columnNames.map((d, i) => (
                                <th key={i}>{d}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {_.slice(dataset, 0, 10).map((row, i) => {
                            return (
                                <tr key={i}>
                                    {summary.columnNames.map((colName, i2) => (
                                        <td key={i2}>{row[colName]}</td>
                                    ))}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
                {summary.numRows > 10 ? (
                    <p>An additional {summary.numRows - 10} rows are not shown...</p>
                ) : null}
            </div>
        );
    }
}
DatasetPreview.propTypes = {
    url: PropTypes.string,
    dataset: PropTypes.array,
};

export default DatasetPreview;
