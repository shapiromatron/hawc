import React, {Component} from "react";
import PropTypes from "prop-types";

class TextInput extends Component {
    renderLabel() {
        if (!this.props.label) {
            return null;
        }
        return (
            <label htmlFor={`id_${this.props.name}`} className="control-label">
                {this.props.label}
                {this.props.required ? <span className="asteriskField">*</span> : null}
            </label>
        );
    }

    render() {
        const type = this.props.type || "text";
        return (
            <div className="control-group">
                {this.renderLabel()}
                <div className="controls">
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
                        <p className="help-block">{this.props.helpText}</p>
                    ) : null}
                </div>
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
