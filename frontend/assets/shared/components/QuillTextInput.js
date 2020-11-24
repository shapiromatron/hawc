import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";

import {errorsDiv, inputClass} from "./inputs";

class QuillTextInput extends Component {
    render() {
        const {errors} = this.props;
        return (
            <div className="form-group">
                <label htmlFor={`id_${this.props.name}`} className="col-form-label">
                    {this.props.label}
                    {this.props.required ? <span className="asteriskField">*</span> : null}
                </label>
                <ReactQuill
                    className={inputClass("col-12 p-0", errors)}
                    id={`id_${this.props.name}`}
                    type="text"
                    required={this.props.required}
                    value={this.props.value}
                    onChange={value => this.props.onChange(value)}
                />
                {errorsDiv(errors)}
                {this.props.helpText ? (
                    <p className="form-text text-muted">{this.props.helpText}</p>
                ) : null}
            </div>
        );
    }
}

QuillTextInput.propTypes = {
    helpText: PropTypes.string,
    errors: PropTypes.array,
    label: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    name: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
};

export default QuillTextInput;
