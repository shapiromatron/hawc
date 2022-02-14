import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {observer} from "mobx-react";
import SelectInput from "shared/components/SelectInput";
import CheckboxInput from "shared/components/CheckboxInput";
import Loading from "shared/components/Loading";
import * as constants from "./constants";

@observer
class DataForm extends Component {
    render() {
        const {store} = this.props,
            {data_source, published_only} = store.settings,
            {stagedDataSettings} = store,
            fetchDataset = () =>
                store.commitStagedDataSettings(data_source != stagedDataSettings.data_source);

        let button = null;
        if (store.isFetchingData) {
            button = <Loading />;
        } else if (
            data_source == stagedDataSettings.data_source &&
            published_only == stagedDataSettings.published_only
        ) {
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
                <button className="btn btn-primary" onClick={fetchDataset}>
                    Fetch dataset
                </button>
            );
        }

        return (
            <div>
                <div className="float-right">{button}</div>
                <legend>Data settings</legend>
                <p className="form-text text-muted">Data settings used to build the table.</p>
                <div className="row">
                    <div className="col-md-6">
                        <SelectInput
                            label="Dataset"
                            choices={constants.dataSourceChoices}
                            multiple={false}
                            handleSelect={value =>
                                store.updateStagedDataSettings({data_source: value})
                            }
                            value={store.stagedDataSettings.data_source}
                        />
                        <p className="form-text text-muted">
                            Select the dataset to use.
                            {store.settings.data_source != store.stagedDataSettings.data_source ? (
                                <span className="text-danger">
                                    <br />
                                    Fetching this dataset will remove current columns and rows.
                                </span>
                            ) : null}
                        </p>
                    </div>
                    <div className="col-md-6">
                        <CheckboxInput
                            label="Published only?"
                            onChange={e =>
                                store.updateStagedDataSettings({published_only: e.target.checked})
                            }
                            helpText="Whether to use only published studies."
                            checked={store.stagedDataSettings.published_only}
                        />
                    </div>
                </div>
                <p className="font-weight-bold">Column choices for this dataset:</p>
                <ul>
                    {_.map(
                        constants.colAttributeChoices[store.stagedDataSettings.data_source],
                        c => (
                            <li key={c.id}>{c.label}</li>
                        )
                    )}
                </ul>
            </div>
        );
    }
}

DataForm.propTypes = {
    store: PropTypes.object,
};
export default DataForm;
