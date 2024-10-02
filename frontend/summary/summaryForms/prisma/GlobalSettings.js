import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
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
            </div>
        );
    }
}
GlobalSettings.propTypes = {
    store: PropTypes.object,
};
export default GlobalSettings;
