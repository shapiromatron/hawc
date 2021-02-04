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
        const inputType = this.props.slider ? "range" : "number";
        return (
            <div className="input-group">
                <input
                    className={fieldClass}
                    min={this.props.minimum}
                    max={this.props.maximum}
                    id={fieldId}
                    name={this.props.name}
                    type={inputType}
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
                    onInput={this.props.onInput}
                />
                {this.props.slider ? (
                    <div className="input-group-append ml-1">
                        <div className="input-group-text">{this.state.value}</div>
                    </div>
                ) : null}
            </div>
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

IntegerInput.defaultProps = {
    slider: false,
    required: false,
};
IntegerInput.propTypes = {
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string,
    maximum: PropTypes.number,
    minimum: PropTypes.number,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    onInput: PropTypes.func,
    required: PropTypes.bool,
    value: PropTypes.number.isRequired,
    slider: PropTypes.bool,
};

export default IntegerInput;
