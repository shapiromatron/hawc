import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import {DataStatusIndicator} from "./common";
import DatasetPreview from "../../summary/heatmap/DatasetPreview";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class DataPanel extends Component {
    render() {
        const {dataError, config, dataset} = this.props.store.base,
            {datasetOptions, settings} = this.props.store.subclass;

        let content;

        if (!datasetOptions) {
            content = <p>Available dataset options loading...</p>;
        } else {
            content = this.renderForm();
        }

        return (
            <div>
                <DataStatusIndicator />
                <legend>Data settings</legend>
                <p className="help-block">
                    Settings which change the data which is used to build the heatmap.
                </p>
                {dataError ? (
                    <div className="alert alert-danger" role="alert">
                        {dataError}
                    </div>
                ) : null}
                {content}
                <hr />
                <DatasetPreview
                    dataset={dataset}
                    url={settings.data_url}
                    clearCacheUrl={config.clear_cache_url}
                />
            </div>
        );
    }
    renderForm() {
        const {settings, changeDatasetUrl, datasetOptions} = this.props.store.subclass;

        return (
            <div>
                <SelectInput
                    name="data_url"
                    label="Data URL"
                    className="col-md-12"
                    choices={datasetOptions}
                    multiple={false}
                    handleSelect={value => changeDatasetUrl(value)}
                    helpText={`Select the dataset you'd like to use. Note that if you select a
                    dataset that contains "unpublished HAWC data", then if this assessment is
                    made public, users without team-level access will be unable to view the visual.`}
                    value={settings.data_url}
                />
            </div>
        );
    }
}

DataPanel.propTypes = {
    store: PropTypes.object,
};
export default DataPanel;
