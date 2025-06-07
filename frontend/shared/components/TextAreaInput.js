import PropTypes from "prop-types";
import React, {Component} from "react";

import HelpText from "./HelpText";
import LabelInput from "./LabelInput";
import {errorsDiv, inputClass} from "./inputs";

class TextInput extends Component {
    renderField(fieldClass, fieldId, errors) {
        return (
            <textarea
                className={inputClass(fieldClass, errors)}
                id={fieldId}
                name={this.props.name}
                type="text"
                required={this.props.required}
                value={this.props.value}
                onChange={this.props.onChange}
            />
        );
    }

    render() {
        let fieldId = this.props.id || this.props.name ? `id_${this.props.name}` : null,
            fieldClass = "form-control",
            {errors} = this.props;
        return (
            <div className="form-group">
                {this.props.label ? <LabelInput for={fieldId} label={this.props.label} /> : null}
                {this.renderField(fieldClass, fieldId, errors)}
                {errorsDiv(errors)}
                {this.props.helpText ? <HelpText text={this.props.helpText} /> : null}
            </div>
        );
    }
}

TextInput.propTypes = {
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.string.isRequired,
    errors: PropTypes.array,
};

export default TextInput;
