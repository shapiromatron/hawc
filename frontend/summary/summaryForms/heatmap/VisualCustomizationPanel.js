import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import TextInput from "shared/components/TextInput";
import {MissingData, RefreshRequired} from "./common";
import SelectInput from "shared/components/SelectInput";
import NumberInput from "shared/components/NumberInput";

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
                    name="title.text"
                    label="Title"
                    value={settings.title.text}
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <TextInput
                    name="x_label.text"
                    label="X label"
                    value={settings.x_label.text}
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <TextInput
                    name="y_label.text"
                    label="Y label"
                    value={settings.y_label.text}
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

                <NumberInput
                    name="padding.top"
                    label="Padding top"
                    value={settings.padding.top}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="padding.left"
                    label="Padding left"
                    value={settings.padding.left}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="padding.bottom"
                    label="Padding bottom"
                    value={settings.padding.bottom}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="padding.right"
                    label="Padding right"
                    value={settings.padding.right}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />

                <NumberInput
                    name="title.x"
                    label="Title x"
                    value={settings.title.x}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="title.y"
                    label="Title y"
                    value={settings.title.y}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="title.rotate"
                    label="Title rotate"
                    value={settings.title.rotate}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />

                <NumberInput
                    name="x_label.x"
                    label="x_Label x"
                    value={settings.x_label.x}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="x_label.y"
                    label="x_Label y"
                    value={settings.x_label.y}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="x_label.rotate"
                    label="x_Label rotate"
                    value={settings.x_label.rotate}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />

                <NumberInput
                    name="y_label.x"
                    label="y_Label x"
                    value={settings.y_label.x}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="y_label.y"
                    label="y_Label y"
                    value={settings.y_label.y}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="y_label.rotate"
                    label="y_Label rotate"
                    value={settings.y_label.rotate}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />

                <NumberInput
                    name="x_tick_rotate"
                    label="x_Tick rotate"
                    value={settings.x_tick_rotate}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <NumberInput
                    name="y_tick_rotate"
                    label="y_Tick rotate"
                    value={settings.y_tick_rotate}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
            </div>
        );
    }
}
VisualCustomizationPanel.propTypes = {
    store: PropTypes.object,
};
export default VisualCustomizationPanel;
