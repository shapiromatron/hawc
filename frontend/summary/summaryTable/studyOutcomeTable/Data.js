import PropTypes from "prop-types";
import React, {Component} from "react";
import {observer} from "mobx-react";
import SelectInput from "shared/components/SelectInput";
import Loading from "shared/components/Loading";
import * as constants from "./constants";

@observer
class DataPanel extends Component {
    render() {
        const {store} = this.props;
        let button = null;
        if (store.isFetchingData) {
            button = <Loading />;
        } else if (store.settings.data_source == store.stagedDataSource) {
            button = store.hasData ? (
                <div className="alert alert-success" role="alert">
                    <i className="fa fa-check-square"></i>&nbsp;Data ready!
                </div>
            ) : (
                <div className="alert alert-danger" role="alert">
                    <i className="fa fa-exclamation-triangle"></i>&nbsp;No data
                </div>
            );
        } else {
            button = (
                <button className="btn btn-primary" onClick={store.commitStagedDataSource}>
                    Fetch data
                </button>
            );
        }

        return (
            <div>
                <div className="float-right">{button}</div>
                <legend>Data settings</legend>
                <p className="form-text text-muted">
                    Settings which change the data which is used to build the table.
                </p>
                <p className="form-text text-warning">
                    Note: Changing the underlying data will remove all columns and rows from your
                    current table.
                </p>

                <div>
                    <SelectInput
                        name="data_url"
                        label="Dataset"
                        choices={constants.dataSourceChoices}
                        multiple={false}
                        handleSelect={value => store.updateStagedDataSource(value)}
                        helpText="Select the dataset you'd like to use."
                        value={store.stagedDataSource}
                    />
                </div>
            </div>
        );
    }
}

DataPanel.propTypes = {
    store: PropTypes.object,
};
export default DataPanel;
