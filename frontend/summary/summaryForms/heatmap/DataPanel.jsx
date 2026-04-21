import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import SelectInput from "shared/components/SelectInput";
import HAWCUtils from "shared/utils/HAWCUtils";

import DatasetPreview from "../../summary/heatmap/DatasetPreview";
import {DataStatusIndicator} from "./common";

const InteractivePopup = props => {
    return (
        <a
            href="/summary/dataset-interactivity/"
            onClick={e => {
                e.preventDefault();
                HAWCUtils.newWindowPopupLink(e.target);
            }}>
            {props.text}
        </a>
    );
};
InteractivePopup.propTypes = {
    text: PropTypes.string.isRequired,
};

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
                <p className="form-text text-muted">
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
                    label="Dataset"
                    choices={datasetOptions}
                    multiple={false}
                    handleSelect={value => changeDatasetUrl(value)}
                    helpText="Select the dataset you'd like to use."
                    value={settings.data_url}
                />
                <ul className="text-muted">
                    <li>
                        If you select a dataset that contains &quot;unpublished HAWC data&quot;,
                        then if this assessment is made public, users without team-level access will
                        be unable to view the visual.
                    </li>
                    <li>
                        With uploaded datasets, if you&nbsp;
                        <InteractivePopup text="design your dataset" /> appropriately, HAWC
                        interactivity is available.
                    </li>
                </ul>
            </div>
        );
    }
}

DataPanel.propTypes = {
    store: PropTypes.object,
};
export default DataPanel;
