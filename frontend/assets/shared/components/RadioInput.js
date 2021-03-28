import React, {Component} from "react";
import PropTypes from "prop-types";

import LabelInput from "./LabelInput";
import HelpText from "./HelpText";

class RadioInput extends Component {
    constructor(props) {
        super(props);
    }

    renderField() {
        return this.props.choices.map(choice => {
            const id = `${this.props.name}-${choice.id}`,
                divClass = this.props.horizontal ? "form-check form-check-inline" : "form-check";
            return (
                <div key={choice.id} className={divClass}>
                    <input
                        className="form-check-input"
                        onChange={() => this.props.onChange(choice.id)}
                        checked={choice.id === this.props.value}
                        type="radio"
                        id={id}
                        name={this.props.name}
                    />
                    <label className="form-check-label" htmlFor={id}>
                        {choice.label}
                    </label>
                </div>
            );
        });
    }

    renderHelpText() {
        return <p className="form-text text-muted">{this.props.helpText}</p>;
    }

    render() {
        return (
            <div className="form-group">
                {this.props.label ? <LabelInput label={this.props.label} /> : null}
                {this.props.horizontal ? <br /> : null}
                {this.renderField()}
                {this.props.helpText ? <HelpText text={this.props.helpText} /> : null}
            </div>
        );
    }
}

RadioInput.propTypes = {
    choices: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.any.isRequired,
            label: PropTypes.string.isRequired,
        })
    ).isRequired,
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string,
    name: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    required: PropTypes.bool.isRequired,
    horizontal: PropTypes.bool,
    value: PropTypes.any.isRequired,
};

RadioInput.defaultProps = {
    required: false,
    horizontal: false,
};

export default RadioInput;
