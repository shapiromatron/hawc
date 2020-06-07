import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import TextInput from "shared/components/TextInput";
import {MissingData, RefreshRequired} from "./common";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class VisualCustomizationPanel extends Component {
    render() {
        const {hasDataset, dataRefreshRequired} = this.props.store.base;
        let content;
        if (!hasDataset) {
            content = <MissingData />;
        } else if (dataRefreshRequired) {
            content = <RefreshRequired />;
        } else {
            content = this.renderForm();
        }
        return (
            <div>
                <legend>Visualization customization</legend>
                <p className="help-block">
                    Customize the look, feel, and layout of the current visual.
                </p>
                {content}
            </div>
        );
    }
    renderForm() {
        const {
            settings,
            changeSettings,
            getColumnsOptions,
            changeSettingsMultiSelect,
        } = this.props.store.subclass;

        return (
            <div>
                <TextInput
                    name="title"
                    label="Title"
                    value={settings.title}
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <TextInput
                    name="x_label"
                    label="X label"
                    value={settings.x_label}
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <TextInput
                    name="y_label"
                    label="Y label"
                    value={settings.y_label}
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <SelectInput
                    name="x_fields"
                    label="X fields"
                    className="span12"
                    choices={getColumnsOptions}
                    multiple={true}
                    handleSelect={value => changeSettingsMultiSelect("x_fields", value)}
                    value={settings.x_fields}
                />
                <SelectInput
                    name="y_fields"
                    label="Y fields"
                    className="span12"
                    choices={getColumnsOptions}
                    multiple={true}
                    handleSelect={value => changeSettingsMultiSelect("y_fields", value)}
                    value={settings.y_fields}
                />
                <SelectInput
                    name="all_fields"
                    label="All fields"
                    className="span12"
                    choices={getColumnsOptions}
                    multiple={true}
                    handleSelect={value => changeSettingsMultiSelect("all_fields", value)}
                    value={settings.all_fields}
                />
            </div>
        );
    }
}
VisualCustomizationPanel.propTypes = {
    store: PropTypes.object,
};
export default VisualCustomizationPanel;
