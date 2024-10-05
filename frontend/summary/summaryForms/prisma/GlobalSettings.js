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
            {styles, box_styles, arrow_styles} = settings;
        return (
            <div className="my-2 p-2 pb-3">
                <h3>Default Style Settings</h3>
                <h4>Section Settings</h4>
                {wrapRow(
                    [
                        <IntegerInput
                            label="Stroke Rounding"
                            key="styles.stroke_radius"
                            name="styles.stroke_radius"
                            value={styles.stroke_radius}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                            helpText="Set the roundness of the corners"
                        />,
                        <IntegerInput
                            label="Stroke Width"
                            key="styles.stroke_width"
                            name="styles.stroke_width"
                            value={styles.stroke_width}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                            helpText="Set the width of the border. Set to 0 for no border"
                        />,
                        <TextInput
                            label="Stroke Color"
                            key="styles.stroke_color"
                            name="styles.stroke_color"
                            value={styles.stroke_color}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                            helpText="Set the color of the border"
                        />,
                        <TextInput
                            key={"styles.bg_color"}
                            name={"styles.bg_color"}
                            value={styles.bg_color}
                            label="Background Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <TextInput
                            key={"styles.font_color"}
                            name={"styles.font_color"}
                            value={styles.font_color}
                            label="Font Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <IntegerInput
                            key={"styles.padding_x"}
                            name={"styles.padding_x"}
                            value={styles.padding_x}
                            label="Text Padding (X axis)"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            helpText="Sets the padding space to the left and right of text elements"
                        />,
                        <IntegerInput
                            key={"styles.padding_y"}
                            name={"styles.padding_y"}
                            value={styles.padding_y}
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
                            key="box_styles.stroke_radius"
                            name="box_styles.stroke_radius"
                            value={box_styles.stroke_radius}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                            helpText="Set the roundness of the corners"
                        />,
                        <IntegerInput
                            label="Stroke Width"
                            key="box_styles.stroke_radius"
                            name="box_styles.stroke_width"
                            value={box_styles.stroke_width}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                            helpText="Set the width of the border. Set to 0 for no border"
                        />,
                        <TextInput
                            label="Stroke Color"
                            key="box_styles.stroke_color"
                            name="box_styles.stroke_color"
                            value={box_styles.stroke_color}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                            helpText="Set the color of the border"
                        />,
                        <TextInput
                            key={"box_styles.bg_color"}
                            name={"box_styles.bg_color"}
                            value={box_styles.bg_color}
                            label="Background Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <TextInput
                            key={"box_styles.font_color"}
                            name={"box_styles.font_color"}
                            value={box_styles.font_color}
                            label="Font Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <IntegerInput
                            key={"box_styles.padding_x"}
                            name={"box_styles.padding_x"}
                            value={box_styles.padding_x}
                            label="Text Padding (X axis)"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            helpText="Sets the padding space to the left and right of text elements"
                        />,
                        <IntegerInput
                            key={"box_styles.padding_y"}
                            name={"box_styles.padding_y"}
                            value={box_styles.padding_y}
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
                            key={"arrow_styles.stroke_width"}
                            name={"arrow_styles.stroke_width"}
                            value={arrow_styles.stroke_width}
                            label="Arrow Width"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />,
                        <SelectInput
                            key={"arrow_styles.arrow_type"}
                            name={"arrow_styles.arrow_type"}
                            value={arrow_styles.arrow_type}
                            label="Arrow Type"
                            handleSelect={value =>
                                changeSettings("arrow_styles.arrow_type", parseInt(value))
                            }
                            choices={getArrowTypes}
                        />,
                        <TextInput
                            key={"arrow_styles.stroke_color"}
                            name={"arrow_styles.stroke_color"}
                            value={arrow_styles.stroke_color}
                            label="Arrow Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <CheckboxInput
                            key={"arrow_styles.force_vertical"}
                            name={"arrow_styles.force_vertical"}
                            checked={arrow_styles.force_vertical}
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
