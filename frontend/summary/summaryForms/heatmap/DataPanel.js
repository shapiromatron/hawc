import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import {DataStatusIndicator} from "./common";
import SelectInput from "shared/components/SelectInput";
@inject("store")
@observer
class DataPanel extends Component {
    render() {
        const {dataError} = this.props.store.base,
            {settings, changeDatasetUrl} = this.props.store.subclass,
            opts = [
                {id: "", label: "<none>"},
                {id: "/ani/api/assessment/1/endpoint-export/?format=json", label: "bioassay"},
                {id: "/assessment/api/dataset/1/data/?format=json", label: "dataset"},
            ];
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
                <SelectInput
                    name="data_url"
                    label="Data URL"
                    className="span12"
                    choices={opts}
                    multiple={false}
                    handleSelect={value => {
                        changeDatasetUrl(value);
                    }}
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
