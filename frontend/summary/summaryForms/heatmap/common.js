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

export {MissingData, RefreshRequired, DataStatusIndicator};
