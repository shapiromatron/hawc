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
                <div className="row-fluid">
                    <div className="span4">
                        <NumberInput
                            name="title.x"
                            label="Title x-coordinate"
                            value={settings.title.x}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span4">
                        <NumberInput
                            name="title.y"
                            label="Title y-coordinate"
                            value={settings.title.y}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span4">
                        <NumberInput
                            name="title.rotate"
                            label="Title rotation"
                            value={settings.title.rotate}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                </div>

                <hr />

                <SelectInput
                    name="x_fields"
                    label="X-axis fields"
                    className="span12"
                    choices={getColumnsOptions}
                    multiple={true}
                    handleSelect={value => changeSettingsMultiSelect("x_fields", value)}
                    value={settings.x_fields}
                />
                <NumberInput
                    name="x_tick_rotate"
                    label="X-axis tick rotation"
                    value={settings.x_tick_rotate}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />

                <TextInput
                    name="x_label.text"
                    label="X-axis label"
                    value={settings.x_label.text}
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <div className="row-fluid">
                    <div className="span4">
                        <NumberInput
                            name="x_label.x"
                            label="X-axis label x-coordinate"
                            value={settings.x_label.x}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span4">
                        <NumberInput
                            name="x_label.y"
                            label="X-axis label y-coordinate"
                            value={settings.x_label.y}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span4">
                        <NumberInput
                            name="x_label.rotate"
                            label="X-axis label rotation"
                            value={settings.x_label.rotate}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                </div>

                <hr />

                <SelectInput
                    name="y_fields"
                    label="Y-axis fields"
                    className="span12"
                    choices={getColumnsOptions}
                    multiple={true}
                    handleSelect={value => changeSettingsMultiSelect("y_fields", value)}
                    value={settings.y_fields}
                />
                <NumberInput
                    name="y_tick_rotate"
                    label="Y-axis tick rotation"
                    value={settings.y_tick_rotate}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <TextInput
                    name="y_label.text"
                    label="Y-axis label"
                    value={settings.y_label.text}
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <div className="row-fluid">
                    <div className="span4">
                        <NumberInput
                            name="y_label.x"
                            label="Y-axis label x-coordinate"
                            value={settings.y_label.x}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span4">
                        <NumberInput
                            name="y_label.y"
                            label="Y-axis label y-coordinate"
                            value={settings.y_label.y}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span4">
                        <NumberInput
                            name="y_label.rotate"
                            label="Y-axis label rotation"
                            value={settings.y_label.rotate}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                </div>

                <hr />

                <SelectInput
                    name="all_fields"
                    label="All fields"
                    className="span12"
                    choices={getColumnsOptions}
                    multiple={true}
                    handleSelect={value => changeSettingsMultiSelect("all_fields", value)}
                    value={settings.all_fields}
                />

                <hr />
                <div className="row-fluid">
                    <div className="span6">
                        <NumberInput
                            name="cell_width"
                            label="Cell width"
                            value={settings.cell_width}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span6">
                        <NumberInput
                            name="cell_height"
                            label="Cell height"
                            value={settings.cell_height}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                </div>

                <hr />

                <div className="row-fluid">
                    <div className="span3">
                        <NumberInput
                            name="padding.top"
                            label="Padding top"
                            value={settings.padding.top}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span3">
                        <NumberInput
                            name="padding.left"
                            label="Padding left"
                            value={settings.padding.left}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span3">
                        <NumberInput
                            name="padding.bottom"
                            label="Padding bottom"
                            value={settings.padding.bottom}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                    <div className="span3">
                        <NumberInput
                            name="padding.right"
                            label="Padding right"
                            value={settings.padding.right}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                </div>
            </div>
        );
    }
}
VisualCustomizationPanel.propTypes = {
    store: PropTypes.object,
};
export default VisualCustomizationPanel;
