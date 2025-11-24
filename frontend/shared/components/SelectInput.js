import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";

import HelpText from "./HelpText";
import {errorsDiv, inputClass} from "./inputs";
import LabelInput from "./LabelInput";

class SelectInput extends Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect(e) {
        let value = e.target.value;
        if (this.props.multiple) {
            value = _.chain(e.target.options)
                .filter(o => o.selected)
                .map(o => o.value)
                .value();
        }
        this.props.handleSelect(value);
    }

    renderField(_fieldClass, fieldId) {
        const value = this.props.value || _.first(this.props.choices).id,
            {errors, className} = this.props;
        return (
            <select
                className={inputClass(className, errors)}
                id={fieldId}
                style={this.props.style}
                value={value}
                onChange={this.handleSelect}
                multiple={this.props.multiple}
                size={this.props.selectSize}
                name={this.props.name}>
                {_.map(this.props.choices, choice => {
                    return (
                        <option key={choice.id} value={choice.id}>
                            {choice.label}
                        </option>
                    );
                })}
            </select>
        );
    }

    render() {
        const fieldId = this.props.id
                ? this.props.id
                : this.props.name
                  ? `id_${this.props.name}`
                  : null,
            {errors} = this.props;

        if (this.props.fieldOnly) {
            return this.renderField(fieldId);
        }
        return (
            <div className="form-group">
                {this.props.label ? <LabelInput for={fieldId} label={this.props.label} /> : null}
                {this.renderField(fieldId)}
                {errorsDiv(errors)}
                {this.props.helpText ? <HelpText text={this.props.helpText} /> : null}
            </div>
        );
    }
}

SelectInput.propTypes = {
    choices: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.any.isRequired,
            label: PropTypes.string.isRequired,
        })
    ).isRequired,
    className: PropTypes.string,
    errors: PropTypes.array,
    fieldOnly: PropTypes.bool,
    handleSelect: PropTypes.func.isRequired,
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string,
    multiple: PropTypes.bool,
    name: PropTypes.string,
    required: PropTypes.bool,
    selectSize: PropTypes.number,
    style: PropTypes.object,
    value: PropTypes.any.isRequired,
};

SelectInput.defaultProps = {
    className: "form-control",
    multiple: false,
};

export default SelectInput;
