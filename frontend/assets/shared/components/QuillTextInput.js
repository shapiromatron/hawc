import React, {Component} from "react";
import PropTypes from "prop-types";
import ReactQuill from "react-quill";

import LabelInput from "./LabelInput";
import HelpText from "./HelpText";

class QuillTextInput extends Component {
    renderField(fieldClass, fieldId) {
        return (
            <ReactQuill
                className={fieldClass}
                id={fieldId}
                type="text"
                required={this.props.required}
                value={this.props.value}
                onChange={value => this.props.onChange(value)}
            />
        );
    }

    render() {
        let fieldId = this.props.id || this.props.name ? `id_${this.props.name}` : null,
            fieldClass = "form-control";
        return (
            <div className="form-group">
                {this.props.label ? <LabelInput for={fieldId} label={this.props.label} /> : null}
                {this.renderField(fieldClass, fieldId)}
                {this.props.helpText ? <HelpText text={this.props.helpText} /> : null}
            </div>
        );
    }
}

QuillTextInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.string.isRequired,
};

export default QuillTextInput;
