import React, {Component} from "react";
import PropTypes from "prop-types";

import LabelInput from "./LabelInput";
import HelpText from "./HelpText";

class TextInput extends Component {
    renderField(fieldClass) {
        return (
            <textarea
                className={fieldClass}
                id={this.props.id}
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

TextInput.propTypes = {
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.string.isRequired,
};

export default TextInput;
