import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import Loading from "shared/components/Loading";

@inject("store")
@observer
class DataFetch extends Component {
    render() {
        const {canFetchData, isFetchingData, isDataReady} = this.props.store.base;

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
                <button
                    className="btn btn-primary"
                    onClick={() => {
                        console.log("go go !");
                    }}>
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
DataFetch.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class DataPanel extends Component {
    render() {
        const {dataError} = this.props.store.base;
        return (
            <div>
                <DataFetch />
                <legend>Data settings</legend>
                <p className="help-block">
                    Settings which change the data which is used to build the heatmap.
                </p>
                {dataError ? (
                    <div className="alert alert-danger" role="alert">
                        {dataError}
                    </div>
                ) : null}
            </div>
        );
    }
}
DataPanel.propTypes = {
    store: PropTypes.object,
};
export default DataPanel;
