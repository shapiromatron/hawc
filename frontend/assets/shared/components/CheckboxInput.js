import React, {Component} from "react";
import PropTypes from "prop-types";
import h from "shared/utils/helpers";

import LabelInput from "./LabelInput";
import HelpText from "./HelpText";

class CheckboxInput extends Component {
    renderField(fieldClass, fieldId) {
        return (
            <input
                className={fieldClass}
                id={fieldId}
                name={this.props.name}
                type="checkbox"
                checked={this.props.checked}
                readOnly={this.props.readOnly || false}
                onChange={this.props.onChange}
            />
        );
    }

    render() {
        let fieldId = `checkbox_${this.props.id ? this.props.id : h.randomString()}`,
            fieldClass = "form-check-input",
            labelClass = "form-check-label";
        return (
            <div className="form-check">
                {this.renderField(fieldClass, fieldId)}
                {this.props.label ? (
                    <LabelInput className={labelClass} for={fieldId} label={this.props.label} />
                ) : null}
                {this.props.helpText ? <HelpText text={this.props.helpText} /> : null}
            </div>
        );
    }
}

CheckboxInput.propTypes = {
    checked: PropTypes.bool.isRequired,
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string,
    name: PropTypes.string,
    onChange: PropTypes.func.isRequired,
    readOnly: PropTypes.bool,
    required: PropTypes.bool,
};

export default CheckboxInput;
