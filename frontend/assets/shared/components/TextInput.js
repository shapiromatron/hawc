import React, {Component} from "react";
import PropTypes from "prop-types";

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
        const type = this.props.type || "text";
        return (
            <div className="form-group">
                {this.renderLabel()}
                <input
                    className="col-md-12 textinput"
                    id={`id_${this.props.name}`}
                    name={this.props.name}
                    type={type}
                    required={this.props.required}
                    value={this.props.value}
                    onChange={this.props.onChange}
                />
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
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.string.isRequired,
    type: PropTypes.string,
};

export default TextInput;
