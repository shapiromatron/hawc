import React, { Component, PropTypes } from 'react';

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
        let { id, defVal, choices } = this.props;
        return (
            <select className='react-select'
                    id={id}
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
    choices: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number.isRequired,
            value: PropTypes.string.isRequired,
        })
    ).isRequired,
    id: PropTypes.string.isRequired,
    defVal: PropTypes.any.isRequired,
};

export default ArraySelect;
