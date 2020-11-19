import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import LabelInput from "./LabelInput";
import HelpText from "./HelpText";
import "./SelectInput.css";

class SelectInput extends Component {
    /**
     * Builds a single <select> input.
     *
     * `Choices` should be an array of objects,
     * with id:int and value:str properties, eg:
     *  [{id: 0, value: 'Option 1'}, {id:1, value: 'Option 1'}];
     */

    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect(e) {
        let value = e.target.value;
        if (this.props.multiple) {
            value = _.chain(event.target.options)
                .filter(o => o.selected)
                .map(o => o.value)
                .value();
        }
        this.props.handleSelect(value);
    }

    renderField(fieldClass, fieldId) {
        let value = this.props.value || _.first(this.props.choices).id;
        return (
            <select
                className={fieldClass}
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
        let fieldId = this.props.id || this.props.name ? `id_${this.props.name}` : null,
            fieldClass = "form-control";
        if (this.props.fieldOnly) {
            return this.renderField("react-select", fieldId);
        }
        return (
            <div className="form-group">
                {this.props.label ? <LabelInput for={fieldId} label={this.props.label} /> : null}
                {this.renderField(fieldClass, fieldId)}
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
    fieldOnly: PropTypes.bool,
    handleSelect: PropTypes.func.isRequired,
    helpText: PropTypes.string,
    id: PropTypes.string,
    label: PropTypes.string,
    multiple: PropTypes.bool.isRequired,
    name: PropTypes.string,
    required: PropTypes.bool,
    selectSize: PropTypes.number,
    style: PropTypes.object,
    value: PropTypes.any.isRequired,
};

export default SelectInput;
