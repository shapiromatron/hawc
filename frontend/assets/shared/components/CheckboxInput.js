import React, {Component} from "react";
import PropTypes from "prop-types";

class CheckboxInput extends Component {
    render() {
        return (
            <div className="form-group">
                <div className="controls">
                    <label htmlFor={this.props.id} className="checkbox">
                        {this.props.label}
                        {this.props.required ? <span className="asteriskField">*</span> : null}
                        <input
                            id={this.props.id}
                            name={this.props.name}
                            type="checkbox"
                            checked={this.props.checked}
                            readOnly={this.props.readOnly || false}
                            onChange={this.props.onChange}
                        />
                    </label>
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
    id: PropTypes.string,
    label: PropTypes.string.isRequired,
    name: PropTypes.string,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    checked: PropTypes.bool.isRequired,
    readOnly: PropTypes.bool,
};

export default CheckboxInput;
