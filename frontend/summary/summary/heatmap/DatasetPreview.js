import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";

import DataTable from "shared/components/DataTable";
import {ActionLink, ActionsButton} from "shared/components/ActionsButton";

class DatasetPreview extends Component {
    render() {
        const {dataset, url, clearCacheUrl} = this.props;

        if (!dataset || dataset.length === 0) {
            return <div className="alert alert-danger">No data are available.</div>;
        }

        const firstRow = dataset[0],
            summary = {
                numRows: dataset.length,
                numColumns: _.keys(firstRow).length,
                columnNames: _.keys(firstRow),
            },
            rowsToShow = 50,
            actionItems = [
                <ActionLink
                    key={0}
                    icon="fa-refresh"
                    label="Clear assessment cache"
                    href={clearCacheUrl}
                />,
                <ActionLink
                    key={1}
                    icon="fa-file-text-o"
                    label="Download dataset (csv)"
                    href={url.includes("?") ? `${url}&format=csv` : `${url}?format=csv`}
                />,
                <ActionLink
                    key={2}
                    icon="fa-file-excel-o"
                    label="Download dataset (xlsx)"
                    href={url.includes("?") ? `${url}&format=xlsx` : `${url}?format=xlsx`}
                />,
            ];

        return (
            <div>
                <ActionsButton items={actionItems} />
                <h4 className="d-inline-block">Dataset overview</h4>
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
                {clearCacheUrl ? (
                    <p className="form-text text-muted">
                        <span className="badge badge-info">Note</span> To improve performance, the
                        data retrieved from this request are cached and reused for future requests.
                        Therefore, changes made to the underlying data are not immediately reflected
                        in visuals (and may take hours to update). To see changes immediately,&nbsp;
                        <a href={clearCacheUrl}>refresh the cache</a>.
                    </p>
                ) : null}
                <h4>
                    {summary.numRows > 0
                        ? `Showing the first ${rowsToShow} rows ...`
                        : "No data available, select a different dataset ..."}
                </h4>
                {summary.numRows > 0 ? (
                    <DataTable dataset={_.slice(dataset, 0, rowsToShow)} />
                ) : null}
                {summary.numRows > rowsToShow ? (
                    <p>An additional {summary.numRows - rowsToShow} rows are not shown...</p>
                ) : null}
            </div>
        );
    }
}
DatasetPreview.propTypes = {
    url: PropTypes.string,
    dataset: PropTypes.array,
    clearCacheUrl: PropTypes.string,
};

export default DatasetPreview;
