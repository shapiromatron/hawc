import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import FloatInput from "shared/components/FloatInput";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";

@inject("store")
@observer
class GlobalSettings extends Component {
    render() {
        const {settings, changeSettings} = this.props.store.subclass,
            {styles} = settings;
        return (
            <div>
                <IntegerInput
                    label="Stroke Rounding"
                    name="styles.stroke_radius"
                    value={styles.stroke_radius}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <IntegerInput
                    label="Stroke Width"
                    name="styles.stroke_width"
                    value={styles.stroke_width}
                    onChange={e => changeSettings(e.target.name, parseInt(e.target.value))}
                />
                <TextInput
                    label="Stroke Color"
                    name="styles.stroke_color"
                    value={styles.stroke_color}
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                    type="color"
                />
                <TextInput
                    name={"styles.bg_color"}
                    value={styles.bg_color}
                    label="Background Color"
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                    type="color"
                />
                <TextInput
                    name={"styles.font_color"}
                    value={styles.font_color}
                    label="Font Color"
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                    type="color"
                />
                <FloatInput
                    name={"styles.font_size"}
                    value={styles.font_size}
                    label="Font size"
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <IntegerInput
                    name={"styles.padding_x"}
                    value={styles.padding_x}
                    label="Padding X"
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
                <IntegerInput
                    name={"styles.padding_y"}
                    value={styles.padding_y}
                    label="Padding Y"
                    onChange={e => changeSettings(e.target.name, e.target.value)}
                />
            </div>
        );
    }
}
GlobalSettings.propTypes = {
    store: PropTypes.object,
};
export default GlobalSettings;
