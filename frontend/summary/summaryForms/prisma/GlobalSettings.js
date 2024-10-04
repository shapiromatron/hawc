import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import FloatInput from "shared/components/FloatInput";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import wrapRow from "shared/components/WrapRow";

@inject("store")
@observer
class GlobalSettings extends Component {
    render() {
        const {settings, changeSettings, getArrowTypes} = this.props.store.subclass,
            {styles, arrow_styles} = settings;
        return (
            <div className="my-2 p-2 pb-3">
                <h3>Default Style Settings</h3>
                <h4>Section and Box Settings</h4>
                {wrapRow(
                    [
                        <IntegerInput
                            label="Stroke Rounding"
                            name="styles.stroke_radius"
                            value={styles.stroke_radius}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />,
                        <IntegerInput
                            label="Stroke Width"
                            name="styles.stroke_width"
                            value={styles.stroke_width}
                            onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                        />,
                        <TextInput
                            label="Stroke Color"
                            name="styles.stroke_color"
                            value={styles.stroke_color}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <TextInput
                            name={"styles.bg_color"}
                            value={styles.bg_color}
                            label="Background Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <TextInput
                            name={"styles.font_color"}
                            value={styles.font_color}
                            label="Font Color"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                            type="color"
                        />,
                        <FloatInput
                            name={"styles.font_size"}
                            value={styles.font_size}
                            label="Font size"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />,
                        <IntegerInput
                            name={"styles.padding_x"}
                            value={styles.padding_x}
                            label="Padding X"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />,
                        <IntegerInput
                            name={"styles.padding_y"}
                            value={styles.padding_y}
                            label="Padding Y"
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />,
                    ],
                    "form-row my-2 mx-2 pad-form"
                )}
                <h4>Arrow Settings</h4>
                {wrapRow([
                    <IntegerInput
                        name={"arrow_styles.stroke_width"}
                        value={arrow_styles.stroke_width}
                        label="Arrow Width"
                        onChange={e => changeSettings(e.target.name, e.target.value)}
                    />,
                    <SelectInput
                        name={"arrow_styles.arrow_type"}
                        value={arrow_styles.arrow_type}
                        label="Arrow Type"
                        handleSelect={value =>
                            changeSettings("arrow_styles.arrow_type", parseInt(value))
                        }
                        choices={getArrowTypes()}
                    />,
                    <TextInput
                        name={"arrow_styles.stroke_color"}
                        value={arrow_styles.stroke_color}
                        label="Arrow Color"
                        onChange={e => changeSettings(e.target.name, e.target.value)}
                        type="color"
                    />,
                    <CheckboxInput
                        name={"arrow_styles.force_vertical"}
                        checked={arrow_styles.force_vertical}
                        label="Force vertical arrow orientation"
                        onChange={e => changeSettings(e.target.name, e.target.checked)}
                    />
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
