import PropTypes from "prop-types";
import React, {Component} from "react";

import HelpText from "./HelpText";
import LabelInput from "./LabelInput";
import {errorsDiv, inputClass} from "./inputs";

class TextInput extends Component {
    renderField(fieldId) {
        const {errors} = this.props;
        return (
            <input
                className={inputClass("form-control", errors)}
                id={fieldId}
                name={this.props.name}
                type={this.props.type || "text"}
                required={this.props.required}
                value={this.props.value}
                onChange={this.props.onChange}
            />
        );
    }

    render() {
        const fieldId = this.props.id || this.props.name ? `id_${this.props.name}` : null,
            {errors} = this.props;
        return (
            <div className="form-group">
                {this.props.label ? <LabelInput for={fieldId} label={this.props.label} /> : null}
                {this.renderField(fieldId)}
                {errorsDiv(errors)}
                {this.props.helpText ? <HelpText text={this.props.helpText} /> : null}
            </div>
        );
    }
}

TextInput.propTypes = {
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    errors: PropTypes.array,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    type: PropTypes.string,
    value: PropTypes.string.isRequired,
};

export default TextInput;
