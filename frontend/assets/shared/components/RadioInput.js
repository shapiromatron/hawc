import React, {Component} from "react";
import PropTypes from "prop-types";

class RadioInput extends Component {
    constructor(props) {
        super(props);
    }

    renderLabel() {
        const {label, required} = this.props;
        if (!label) {
            return null;
        }
        return (
            <label className="col-form-label">
                {label}
                {required ? <span className="asteriskField">*</span> : null}
            </label>
        );
    }

    render() {
        const {name, value, onChange, choices, helpText} = this.props;
        return (
            <div className="form-group">
                {this.renderLabel()}
                {choices.map(choice => {
                    const id = `${name}-${choice.id}`;
                    return (
                        <label key={choice.id} className="form-check" htmlFor={id}>
                            <input
                                onChange={event => onChange(name, choice.id)}
                                checked={choice.id === value}
                                type="radio"
                                id={id}
                                name={name}
                            />
                            {choice.label}
                        </label>
                    );
                })}

                {helpText ? <p className="form-text text-muted">{helpText}</p> : null}
            </div>
        );
    }
}

RadioInput.propTypes = {
    helpText: PropTypes.string,
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    required: PropTypes.bool.isRequired,
    onChange: PropTypes.func.isRequired,
    value: PropTypes.any.isRequired,
    choices: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.any.isRequired,
            label: PropTypes.string.isRequired,
        })
    ).isRequired,
};

RadioInput.defaultProps = {
    required: false,
};

export default RadioInput;
