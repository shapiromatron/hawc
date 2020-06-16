import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import {DataStatusIndicator, DatasetProperties} from "./common";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class DataPanel extends Component {
    render() {
        const {dataError, dataset, datasetSummary} = this.props.store.base,
            {datasetOptions} = this.props.store.subclass;

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
                <DatasetProperties dataset={dataset} summary={datasetSummary} />
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
                    className="span12"
                    choices={datasetOptions}
                    multiple={false}
                    handleSelect={value => changeDatasetUrl(value)}
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
