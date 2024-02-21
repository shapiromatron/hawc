import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Alert from "shared/components/Alert";
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
            component = <Alert message="No dataset selected; please edit settings..." />;
        }
        return <div className="float-right">{component}</div>;
    }
}
DataStatusIndicator.propTypes = {
    store: PropTypes.object,
};

const HelpText = {
    customItems: `By default, items are presented in alphabetical order.
        If customized, users can customize the order of display.`,
    delimiter: `If data are delimited in a cell, the delimiter character used.
        If unspecified, the data are not delimited`,
    header: `By default the data column name is shown as the header;
        this can be overridden with custom text here.`,
    wrapText: "Wrap text at a specified length, else auto calculated",
};

export {DataStatusIndicator, HelpText, MissingData, RefreshRequired};
