import React, {Component} from "react";
import PropTypes from "prop-types";

import LabelInput from "./LabelInput";
import HelpText from "./HelpText";
import HelpTextPopup from "./HelpTextPopup";

class IntegerInput extends Component {
    constructor(props) {
        super(props);
        this.state = {
            value: props.value.toString(),
        };
    }

    renderField(fieldClass, fieldId) {
        const inputType = this.props.slider ? "range" : "number",
            {minimum, maximum, required} = this.props,
            getStrValue = valueString => {
                const valueInt = parseInt(valueString);
                if (
                    isNaN(valueInt) ||
                    (minimum && valueInt < minimum) ||
                    (maximum && valueInt > maximum)
                ) {
                    return required ? this.props.value.toString() : "";
                }
                return valueInt.toString();
            };
        return (
            <div className="input-group">
                <input
                    className={fieldClass}
                    min={minimum}
                    max={maximum}
                    id={fieldId}
                    name={this.props.name}
                    type={inputType}
                    required={this.props.required}
                    value={this.state.value}
                    onBlur={e => this.setState({value: getStrValue(e.target.value)})}
                    onChange={e => {
                        this.setState({value: getStrValue(e.target.value)});
                        this.props.onChange(e);
                    }}
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
                {this.props.helpPopup ? <HelpTextPopup content={this.props.helpPopup} /> : null}
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
    helpPopup: PropTypes.string,
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
