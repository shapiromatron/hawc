import React, {Component} from "react";
import PropTypes from "prop-types";

import {errorsDiv, inputClass} from "./inputs";

class TextInput extends Component {
    renderLabel() {
        if (!this.props.label) {
            return null;
        }
        return (
            <label htmlFor={`id_${this.props.name}`} className="col-form-label">
                {this.props.label}
                {this.props.required ? <span className="asteriskField">*</span> : null}
            </label>
        );
    }

    render() {
        const type = this.props.type || "text",
            {errors} = this.props;
        return (
            <div className="form-group">
                {this.renderLabel()}
                <input
                    className={inputClass("form-control", errors)}
                    id={`id_${this.props.name}`}
                    name={this.props.name}
                    type={type}
                    required={this.props.required}
                    value={this.props.value}
                    onChange={this.props.onChange}
                />
                {errorsDiv(errors)}
                {this.props.helpText ? (
                    <p className="form-text text-muted">{this.props.helpText}</p>
                ) : null}
            </div>
        );
    }
}

TextInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    errors: PropTypes.array,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.string.isRequired,
    type: PropTypes.string,
};

export default TextInput;
