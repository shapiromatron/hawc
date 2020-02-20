import React, {Component} from "react";
import PropTypes from "prop-types";

const noop = e => {
    console.log("None");
};

class CheckboxInput extends Component {
    render() {
        return (
            <div className="control-group">
                <label htmlFor={`id_${this.props.name}`} className="control-label">
                    {this.props.label}
                    {this.props.required ? <span className="asteriskField">*</span> : null}
                </label>
                <div className="controls">
                    <input
                        id={`id_${this.props.name}`}
                        name={this.props.name}
                        type="checkbox"
                        checked={this.props.checked}
                        readOnly={this.props.readOnly || false}
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

CheckboxInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    checked: PropTypes.bool.isRequired,
    readOnly: PropTypes.readOnly,
};

export default CheckboxInput;
