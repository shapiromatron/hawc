import PropTypes from "prop-types";
import React, {Component} from "react";

class LabelInput extends Component {
    render() {
        return (
            <label htmlFor={this.props.for} className={this.props.className}>
                {this.props.label}
                {this.props.required ? <span className="asteriskField">*</span> : null}
            </label>
        );
    }
}

LabelInput.propTypes = {
    className: PropTypes.string,
    for: PropTypes.string,
    label: PropTypes.string,
    required: PropTypes.bool,
};

export default LabelInput;
