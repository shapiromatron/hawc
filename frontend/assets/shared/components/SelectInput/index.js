import React, {Component} from "react";
import PropTypes from "prop-types";
import _ from "lodash";

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

    renderLabel() {
        if (!this.props.label) {
            return null;
        }
        return (
            <label htmlFor={`id_${this.props.name}`} className="control-label">
                {this.props.label}
                {this.props.required ? <span className="asteriskField">*</span> : null}
            </label>
        );
    }

    renderField() {
        let {id, choices, name, multiple, selectSize} = this.props,
            className = this.props.className || "react-select",
            value = this.props.value || _.first(choices).id;

        return (
            <select
                id={id || null}
                className={className}
                value={value}
                onChange={this.handleSelect}
                multiple={multiple}
                size={selectSize}
                name={name}>
                {_.map(choices, choice => {
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
        let {fieldOnly, helpText} = this.props;
        if (fieldOnly) {
            return this.renderField();
        }
        return (
            <div className="controls">
                <div className="control-group">
                    {this.renderLabel()}
                    {this.renderField()}
                    {helpText ? <p className="help-block">{this.props.helpText}</p> : null}
                </div>
            </div>
        );
    }
}

SelectInput.propTypes = {
    handleSelect: PropTypes.func.isRequired,
    className: PropTypes.string,
    choices: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.any.isRequired,
            label: PropTypes.string.isRequired,
        })
    ).isRequired,
    id: PropTypes.string,
    value: PropTypes.any.isRequired,
    name: PropTypes.string,
    multiple: PropTypes.bool.isRequired,
    selectSize: PropTypes.number,
    helpText: PropTypes.string,
    label: PropTypes.string,
    required: PropTypes.bool,
    fieldOnly: PropTypes.bool,
};

export default SelectInput;
