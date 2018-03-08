import React, { Component } from 'react';
import PropTypes from 'prop-types';

class TextInput extends Component {
    render() {
        return (
            <div className="control-group">
                <label htmlFor={`id_${this.props.name}`} className="control-label">
                    {this.props.label}
                    {this.props.required ? <span className="asteriskField">*</span> : null}
                </label>
                <div className="controls">
                    <input
                        className="span12 textinput"
                        id={`id_${this.props.name}`}
                        name={this.props.name}
                        type="text"
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
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.string.isRequired,
};

export default TextInput;
