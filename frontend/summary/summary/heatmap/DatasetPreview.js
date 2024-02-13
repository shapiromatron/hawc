import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionLink, ActionsButton} from "shared/components/ActionsButton";
import Alert from "shared/components/Alert";
import DataTable from "shared/components/DataTable";

class DatasetPreview extends Component {
    render() {
        const {dataset, url, clearCacheUrl} = this.props;

        if (!dataset || dataset.length === 0) {
            return <Alert message={"No data are available."} />;
        }

        const firstRow = dataset[0],
            summary = {
                numRows: dataset.length,
                numColumns: _.keys(firstRow).length,
                columnNames: _.keys(firstRow),
            },
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
                <div className="d-flex">
                    <h4>Dataset overview</h4>
                    <ActionsButton items={actionItems} />
                </div>
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
                        ? "Data preview"
                        : "No data available, select a different dataset ..."}
                </h4>
                {summary.numRows > 0 ? (
                    <div className="overflow-auto">
                        <DataTable dataset={dataset} tablesort={false} datatables={true} />
                    </div>
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
