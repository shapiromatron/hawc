import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactQuill from "react-quill";

import HelpText from "./HelpText";
import LabelInput from "./LabelInput";
import {errorsDiv, inputClass} from "./inputs";

class QuillTextInput extends Component {
    renderField(fieldId) {
        const {errors, className} = this.props,
            extraClasses = className ? `${this.props.className} ` : "";

        return (
            <ReactQuill
                id={fieldId}
                className={inputClass(`${extraClasses}col-12 p-0`, errors)}
                type="text"
                required={this.props.required}
                value={this.props.value}
                onChange={value => this.props.onChange(value)}
            />
        );
    }

    render() {
        const {errors} = this.props,
            fieldId = this.props.id || this.props.name ? `id_${this.props.name}` : null;
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

QuillTextInput.propTypes = {
    helpText: PropTypes.string,
    errors: PropTypes.array,
    id: PropTypes.string,
    label: PropTypes.string,
    name: PropTypes.string,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.string.isRequired,
    className: PropTypes.string,
};

export default QuillTextInput;
