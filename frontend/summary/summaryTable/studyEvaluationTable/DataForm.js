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
                            label="Select dataset"
                            choices={constants.dataSourceChoices}
                            multiple={false}
                            handleSelect={v => store.updateStagedDataSettings({data_source: v})}
                            value={store.stagedDataSettings.data_source}
                        />
                        <p className="form-text text-muted">
                            Select the dataset to use. Data are filtered to only include studies
                            where at least one final study evaluation exists.
                            {store.settings.data_source != store.stagedDataSettings.data_source ? (
                                <span className="text-danger">
                                    <br />
                                    Fetching this dataset will remove current columns and rows.
                                </span>
                            ) : null}
                        </p>
                    </div>
                    <div className="col-md-6">
                        <p className="font-weight-bold mb-0">Column choices selected dataset:</p>
                        <ul>
                            {_.map(
                                constants.colAttributeChoices[store.stagedDataSettings.data_source],
                                c => (
                                    <li key={c.id}>{c.label}</li>
                                )
                            )}
                        </ul>
                    </div>
                    <div className="col-md-6">
                        <CheckboxInput
                            label="Published studies only"
                            onChange={e =>
                                store.updateStagedDataSettings({published_only: e.target.checked})
                            }
                            helpText='Only present data from studies which have been marked as "published" in HAWC. Make sure to change prior to making an assessment public; otherwise users who are not team members will not be able to view this table.'
                            checked={store.stagedDataSettings.published_only}
                        />
                    </div>
                </div>
            </div>
        );
    }
}

DataForm.propTypes = {
    store: PropTypes.object,
};
export default DataForm;
