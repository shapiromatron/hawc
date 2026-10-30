import PropTypes from "prop-types";
import React, {Component} from "react";

import HelpText from "./HelpText";
import LabelInput from "./LabelInput";

class FloatInput extends Component {
    constructor(props) {
        super(props);
        this.state = {
            value: props.value.toString(),
        };
    }

    renderField(fieldClass, fieldId) {
        return (
            <input
                className={fieldClass}
                id={fieldId}
                name={this.props.name}
                type="text"
                required={this.props.required}
                value={this.state.value}
                onBlur={e => {
                    let valueString = e.target.value,
                        valueFloat = parseFloat(valueString);
                    if (
                        isNaN(valueFloat) ||
                        (this.props.minimum && valueFloat < this.props.minimum) ||
                        (this.props.maximum && valueFloat > this.props.maximum)
                    ) {
                        this.setState({value: this.props.value.toString()});
                    } else {
                        this.props.onChange(e);
                        this.setState({value: valueFloat.toString()});
                    }
                }}
                onChange={e => this.setState({value: e.target.value})}
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

FloatInput.propTypes = {
    helpText: PropTypes.string,
    horizontal: PropTypes.bool,
    id: PropTypes.string,
    label: PropTypes.string,
    maximum: PropTypes.number,
    minimum: PropTypes.number,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.number.isRequired,
};

export default FloatInput;
