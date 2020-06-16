import _ from "lodash";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import Loading from "shared/components/Loading";

class MissingData extends Component {
    render() {
        return (
            <div className="alert alert-warning" role="alert">
                Data is missing; update settings on the Data tab and press &quot;Fetch data&quot;.
            </div>
        );
    }
}

class RefreshRequired extends Component {
    render() {
        return (
            <div className="alert alert-warning" role="alert">
                A data refresh is required; press &quot;Fetch data&quot; on settings page.
            </div>
        );
    }
}

@inject("store")
@observer
class DataStatusIndicator extends Component {
    render() {
        const {canFetchData, isFetchingData, isDataReady, getDataset} = this.props.store.base;

        let component = null;
        if (isDataReady) {
            component = (
                <div className="alert alert-success" role="alert">
                    <i className="fa fa-check-square"></i>&nbsp;Data ready!
                </div>
            );
        } else if (isFetchingData) {
            component = <Loading />;
        } else if (canFetchData) {
            component = (
                <button className="btn btn-primary" onClick={getDataset}>
                    Fetch data
                </button>
            );
        } else {
            component = (
                <div className="alert alert-danger" role="alert">
                    <i className="fa fa-close"></i>&nbsp;No data; please edit settings...
                </div>
            );
        }
        return <div className="pull-right">{component}</div>;
    }
}
DataStatusIndicator.propTypes = {
    store: PropTypes.object,
};

class DatasetProperties extends Component {
    render() {
        const {summary, dataset} = this.props;

        if (!summary) {
            return null;
        }

        return (
            <div>
                <h4>Dataset overview</h4>
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
DatasetProperties.propTypes = {
    dataset: PropTypes.array,
    summary: PropTypes.object,
};

export {MissingData, RefreshRequired, DataStatusIndicator, DatasetProperties};
