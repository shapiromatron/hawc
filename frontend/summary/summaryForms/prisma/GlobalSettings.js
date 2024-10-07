import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import wrapRow from "shared/components/WrapRow";

@inject("store")
@observer
class GlobalSettings extends Component {
    render() {
        const {settings, changeSettings, getArrowTypes} = this.props.store.subclass,
            {styles} = settings;
        return (
            <div className="my-2 p-2 pb-3">
                <h3>Default Style Settings</h3>
                <p className="text-muted">
                    Configure overall styling for all visual components. You can manually configure
                    any individual component overrides, but these are the default settings for all
                    items in the visualization.
                </p>
                <h4>Section Settings</h4>
                {wrapRow(
                    [
                        <IntegerInput
                            label="Stroke Rounding"
                            key="styles.section.stroke_radius"
                            name="styles.section.stroke_radius"
                            value={styles.section.stroke_radius}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                            helpText="Set the roundness of the corners"
                        />,
                        <IntegerInput
                            label="Stroke Width"
                            key="styles.section.stroke_width"
                            name="styles.section.stroke_width"
                            value={styles.section.stroke_width}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                            helpText="Set the width of the border. Set to 0 for no border"
                        />,
                        <TextInput
                            label="Stroke Color"
                            key="styles.section.stroke_color"
                            name="styles.section.stroke_color"
                            value={styles.section.stroke_color}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                            helpText="Set the color of the border"
                        />,
                        <TextInput
                            key={"styles.section.bg_color"}
                            name={"styles.section.bg_color"}
                            value={styles.section.bg_color}
                            label="Background Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <TextInput
                            key={"styles.section.font_color"}
                            name={"styles.section.font_color"}
                            value={styles.section.font_color}
                            label="Font Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <IntegerInput
                            key={"styles.section.padding_x"}
                            name={"styles.section.padding_x"}
                            value={styles.section.padding_x}
                            label="Text Padding (X axis)"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            helpText="Sets the padding space to the left and right of text elements"
                        />,
                        <IntegerInput
                            key={"styles.section.padding_y"}
                            name={"styles.section.padding_y"}
                            value={styles.section.padding_y}
                            label="Text Padding (Y axis)"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            helpText="Sets the padding space above and below text elements"
                        />,
                    ],
                    "form-row my-2 mx-2 pad-form"
                )}
                <h4>Box Settings</h4>
                {wrapRow(
                    [
                        <IntegerInput
                            label="Stroke Rounding"
                            key="styles.box.stroke_radius"
                            name="styles.box.stroke_radius"
                            value={styles.box.stroke_radius}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                            helpText="Set the roundness of the corners"
                        />,
                        <IntegerInput
                            label="Stroke Width"
                            key="styles.box.stroke_radius"
                            name="styles.box.stroke_width"
                            value={styles.box.stroke_width}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                            helpText="Set the width of the border. Set to 0 for no border"
                        />,
                        <TextInput
                            label="Stroke Color"
                            key="styles.box.stroke_color"
                            name="styles.box.stroke_color"
                            value={styles.box.stroke_color}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                            helpText="Set the color of the border"
                        />,
                        <TextInput
                            key={"styles.box.bg_color"}
                            name={"styles.box.bg_color"}
                            value={styles.box.bg_color}
                            label="Background Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <TextInput
                            key={"styles.box.font_color"}
                            name={"styles.box.font_color"}
                            value={styles.box.font_color}
                            label="Font Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <IntegerInput
                            key={"styles.box.padding_x"}
                            name={"styles.box.padding_x"}
                            value={styles.box.padding_x}
                            label="Text Padding (X axis)"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            helpText="Sets the padding space to the left and right of text elements"
                        />,
                        <IntegerInput
                            key={"styles.box.padding_y"}
                            name={"styles.box.padding_y"}
                            value={styles.box.padding_y}
                            label="Text Padding (Y axis)"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            helpText="Sets the padding space above and below text elements"
                        />,
                    ],
                    "form-row my-2 mx-2 pad-form"
                )}
                <h4>Arrow Settings</h4>
                {wrapRow(
                    [
                        <IntegerInput
                            key={"styles.arrow.stroke_width"}
                            name={"styles.arrow.stroke_width"}
                            value={styles.arrow.stroke_width}
                            label="Arrow Width"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />,
                        <SelectInput
                            key={"styles.arrow.arrow_type"}
                            name={"styles.arrow.arrow_type"}
                            value={styles.arrow.arrow_type}
                            label="Arrow Type"
                            handleSelect={value =>
                                changeSettings("styles.arrow.arrow_type", parseInt(value))
                            }
                            choices={getArrowTypes}
                        />,
                        <TextInput
                            key={"styles.arrow.stroke_color"}
                            name={"styles.arrow.stroke_color"}
                            value={styles.arrow.stroke_color}
                            label="Arrow Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <CheckboxInput
                            key={"styles.arrow.force_vertical"}
                            name={"styles.arrow.force_vertical"}
                            checked={styles.arrow.force_vertical}
                            label="Force vertical arrow orientation"
                            onChange={e => changeSettings(e.target.name, e.target.checked)}
                        />,
                    ],
                    "form-row my-2 mx-2 pad-form"
                )}
            </div>
        );
    }
}
GlobalSettings.propTypes = {
    store: PropTypes.object,
};
export default GlobalSettings;
