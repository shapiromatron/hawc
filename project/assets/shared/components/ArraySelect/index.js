import React, { Component } from 'react';
import PropTypes from 'prop-types';

import './ArraySelect.css';


class ArraySelect extends Component {
    /**
     * The choices props should be an array of objects, with id and value properties
     *
     * choices = [{id: 0, value: 'Option 1'}, {id:1, value: 'Option 1'}];
     */

    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect(e){
        this.props.handleSelect(e.target.value);
    }

    render() {
        let { id, choices } = this.props,
            className = this.props.className || 'react-select',
            defVal = this.props.defVal || _.first(choices);
        return (
            <select id={id}
                    className={className}
                    ref='select'
                    defaultValue={defVal}
                    onChange={this.handleSelect}>
                {_.map(choices, (choice) => {
                    return <option key={choice.id} value={choice.id}>{choice.value}</option>;
                })}
            </select>
        );
    }
}

ArraySelect.propTypes = {
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
};

export default ArraySelect;
