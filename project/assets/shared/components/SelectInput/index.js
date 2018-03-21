import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import './SelectInput.css';

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
        this.props.handleSelect(e.target.value);
    }

    render() {
        let { id, choices, name } = this.props,
            className = this.props.className || 'react-select',
            value = this.props.value || this.props.defVal || _.first(choices);
        return (
            <select
                id={id}
                className={className}
                value={value}
                onChange={this.handleSelect}
                name={name}
            >
                {_.map(choices, (choice) => {
                    return (
                        <option key={choice.id} value={choice.id}>
                            {choice.value}
                        </option>
                    );
                })}
            </select>
        );
    }
}

SelectInput.propTypes = {
    handleSelect: PropTypes.func.isRequired,
    className: PropTypes.string,
    choices: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            value: PropTypes.string.isRequired,
        })
    ).isRequired,
    id: PropTypes.string.isRequired,
    defVal: PropTypes.any,
    value: PropTypes.any,
    name: PropTypes.string,
};

export default SelectInput;
