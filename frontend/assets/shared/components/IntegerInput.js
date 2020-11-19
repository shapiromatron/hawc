import React, {Component} from "react";
import PropTypes from "prop-types";

import LabelInput from "./LabelInput";
import HelpText from "./HelpText";

class IntegerInput extends Component {
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
                type="number"
                required={this.props.required}
                value={this.state.value}
                onBlur={e => {
                    let valueString = e.target.value,
                        valueInt = parseInt(valueString);
                    if (
                        isNaN(valueInt) ||
                        (this.props.minimum && valueInt < this.props.minimum) ||
                        (this.props.maximum && valueInt > this.props.maximum)
                    ) {
                        this.setState({value: this.props.value.toString()});
                    } else {
                        this.props.onChange(e);
                        this.setState({value: valueInt.toString()});
                    }
                }}
                onChange={e => this.setState({value: e.target.value})}
            />
        );
    }

    render() {
        let fieldId = this.props.id || this.props.name ? `id_${this.props.name}` : null,
            fieldClass = "form-check-input";
        return (
            <div className="form-group">
                {this.props.label ? <LabelInput for={fieldId} label={this.props.label} /> : null}
                {this.renderField(fieldClass, fieldId)}
                {this.props.helpText ? <HelpText text={this.props.helpText} /> : null}
            </div>
        );
    }
}

IntegerInput.propTypes = {
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string,
    maximum: PropTypes.number,
    minimum: PropTypes.number,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool,
    value: PropTypes.number.isRequired,
};

export default IntegerInput;
